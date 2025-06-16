import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from sqlalchemy import asc, desc, select, func
from app.persistence.categories.categories import Category
from app.persistence.transactions.transaction import Transaction
from app.persistence.recurring_transactions.recurring_transaction import RecurringTransaction
from app.persistence.balances.balance import Balance
from app.persistence.users.users import User
from app.schemas.transaction import TransactionCreate
from app.services.cards_service import get_card_by_number
from app.services.currencies_service import get_currency_id_by_code
from app.services.users_service import *
from app.schemas.category import CategoryCreate
from app.services.categories_service import _get_category_id_by_name, create_category, get_category_by_name
from app.core.enums.enums import IntervalType, TransactionType
from app.services.categories_service import create_category

from uuid import UUID
from datetime import date
from decimal import Decimal

from app.services.users_service import _get_user_by_id


async def create_user_to_user_transaction(db: AsyncSession, sender_id: UUID, transaction_data: TransactionCreate):
    
    sender = await _get_user_by_id(db, sender_id)
                                     
    if not sender.is_activated:
        raise HTTPException(403, "Sender account is not activated")
    
    # if not sender.is_verified:
    #     raise HTTPException(403, "Sender account is not verified")

    card = await get_card_by_number(db, transaction_data.card_number)
    if not card.balance:
        raise HTTPException(status_code=400, detail="Card has no balance")
    if card.balance.user_id != sender_id:
        raise HTTPException(status_code=403, detail="Card does not belong to sender")
    
    sender_balance = card.balance
    await ensure_sufficient_funds(sender_balance, transaction_data.amount)
    
    receiver = await get_receiver_by_username(db, transaction_data.receiver_username)
    if receiver.id == sender_id:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")
    
    currency_id = await get_currency_id_by_code(db=db, code=transaction_data.currency_code)

    await get_or_create_receiver_balance(db, receiver.id, currency_id)
    
    if transaction_data.predefined_category:
        category_id = await _get_category_id_by_name(transaction_data.predefined_category)
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
    elif transaction_data.category_name:
        result = await db.execute(select(Category).where(Category.name == transaction_data.category_name, Category.user_id == sender_id))
        category = result.scalar_one_or_none()

        if not category:
            category_create = CategoryCreate(name=transaction_data.category_name, user_id=sender_id)
            category = await create_category(db, sender_id, category_create)
            category_id = category.id
    else:
        raise HTTPException(status_code=400, detail="Category must be specified from the predefined list or created by name")

    if transaction_data.is_recurring:
        if not transaction_data.interval_days or not transaction_data.next_run_date:
            raise HTTPException(status_code=400, detail="Recurring transactions must have interval type and next execution date")
        interval_type = IntervalType.get_interval_type_from_days(transaction_data.interval_days)
        await create_recurring_transaction(
            db=db,
            sender_id=sender_id,
            receiver_id=receiver.id,
            amount=transaction_data.amount,
            currency_id=currency_id,
            interval_type=interval_type,
            next_run_date=transaction_data.next_run_date,
            description=transaction_data.description,
        )

    transaction = Transaction(
        sender_id=sender_id,
        receiver_id=receiver.id,
        currency_id=currency_id,
        category_id=category_id,
        amount=transaction_data.amount,
        status="pending",
        is_recurring=transaction_data.is_recurring,
        created_date=date.today(),
        description=transaction_data.description,
        sender_card_id=card.id,
        receiver_card_id=None, 
        transaction_type=TransactionType.USER_TO_ANOTHER_USER
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


async def accept_transaction(db: AsyncSession, transaction_id: UUID):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="Transaction already processed")
    
    stmt_sender = select(Balance).where(
        Balance.user_id == transaction.sender_id, 
        Balance.currency_id == transaction.currency_id)
    result = await db.execute(stmt_sender)
    sender_balance = result.scalar_one_or_none()
    if not sender_balance:
        raise HTTPException(status_code=404, detail="No balance in this currency")
    
    stmt_receiver = select(Balance).where(
        Balance.user_id == transaction.receiver_id,
        Balance.currency_id == transaction.currency_id
    )
    result = await db.execute(stmt_receiver)
    receiver_balance = result.scalar_one_or_none()
    if not receiver_balance:
        receiver_balance = Balance(
            user_id=transaction.receiver_id,
            currency_id=transaction.currency_id,
            amount=Decimal("0.0")
        )
        db.add(receiver_balance)
        await db.flush()
    
    if sender_balance.amount < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds at approval time")

    sender_balance.amount -= transaction.amount
    receiver_balance.amount += transaction.amount

    transaction.status = "completed"
    await db.commit()
    await db.refresh(transaction)

    return transaction


async def deactivate_recurring_transaction(db: AsyncSession, transaction_id: UUID):
    result = await db.execute(select(RecurringTransaction).where(RecurringTransaction.id == transaction_id))
    recurring_transaction = result.scalar_one_or_none()
    if recurring_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    recurring_transaction.is_active = False
    await db.commit()
    await db.refresh(recurring_transaction)
    return recurring_transaction


async def view_all_transactions(db:AsyncSession, skip: int = 0, limit: int = 5, sort_by: str = "date", sort_order: str = "asc"):
    sort = {"date": Transaction.created_date,
            "amount": Transaction.amount}[sort_by]
    order_func = asc if sort_order == "asc" else desc
    total_query = await db.execute(select(func.count()).select_from(Transaction))
    total = total_query.scalar_one()
    result = await db.execute(select(Transaction).order_by(order_func(sort)).offset(skip).limit(limit))
    transactions = result.scalars().all()

    current_page = (skip // limit) + 1
    has_next = skip + limit < total

    return {
        "transactions":transactions,
        "total":total,
        "has_next": has_next,
        "page":current_page,
        "per_page":limit
        }


async def view_all_recurring_transactions(db: AsyncSession, skip: int = 0, limit: int = 5):
    total_query = await db.execute(select(func.count()).select_from(RecurringTransaction))
    total = total_query.scalar_one()
    result = await db.execute(select(RecurringTransaction).offset(skip).limit(limit))
    recurring_transactions = result.scalars().all()

    current_page = (skip // limit) + 1
    has_next = skip + limit < total

    return {
        "recurring_transactions": recurring_transactions,
        "total": total,
        "has_next": has_next,
        "page": current_page,
        "per_page": limit
    }

async def reject_transaction(db: AsyncSession, transaction_id: UUID):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="Transaction already processed")
    
    transaction.status = "rejected"
    await db.commit()
    await db.refresh(transaction)

    return transaction


async def get_receiver(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    receiver = result.scalar_one_or_none()
    if not receiver:
        raise HTTPException(status_code=404, detail= "User not found")
    return receiver

async def get_user_balance(db:AsyncSession, user_id: UUID, currency_id: UUID):
    result = await db.execute(select(Balance).where(Balance.user_id == user_id, Balance.currency_id == currency_id))
    balance = result.scalar_one_or_none()
    if not balance:
        raise HTTPException(status_code=404, detail= "Balance not found")
    return balance

async def ensure_sufficient_funds(balance: Balance, amount: Decimal):
    if balance.amount < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
async def get_or_create_receiver_balance(db: AsyncSession, user_id: UUID, currency_id: UUID):
    try:
        balance = await get_user_balance(db, user_id, currency_id)
    except HTTPException as e:
        if e.status_code == 404:
            balance = Balance(user_id = user_id,
                          currency_id = currency_id,
                          amount = Decimal("0.0"))
            db.add(balance)
            await db.flush()
        else:
            raise e
    return balance

async def get_or_create_category(db: AsyncSession, category_id: uuid.UUID | None = None, category_name: str | None = None):
    if category_id:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
    elif category_name:
        result = await db.execute(select(Category).where(Category.name == category_name))
        category = result.scalar_one_or_none()
        if not category:
            category = Category(name = category_name)
            db.add(category)
            await db.flush()
    else:
        raise HTTPException(status_code=404, detail="Category must be specified by id or name")
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

async def get_receiver_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def create_recurring_transaction(
    db: AsyncSession,
    sender_id: UUID,
    receiver_id: UUID,
    amount: Decimal,
    currency_id: UUID,
    interval_type: IntervalType,
    next_run_date: date | None,
    description: str | None = None,
):
    recurring_transaction = RecurringTransaction(
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        currency_id=currency_id,
        interval_type=interval_type,
        next_execution_date=next_run_date or date.today(),
        description=description or "",
        is_active=True,
        last_run_date=None
    )
    db.add(recurring_transaction)
    await db.flush()
    return recurring_transaction

async def transfer_between_cards(db: AsyncSession, sending_card_number: str, receiving_card_number: str, amount: Decimal, description: str | None = None):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    sending_card = await get_card_by_number(db, sending_card_number)
    if not sending_card:
        raise HTTPException(status_code=404, detail=f"Sending card {sending_card_number} not found")

    receiving_card = await get_card_by_number(db, receiving_card_number)
    if not receiving_card:
        raise HTTPException(status_code=404, detail=f"Receiving card {receiving_card_number} not found")

    
    sending_card = await get_card_by_number(db, sending_card_number)
    receiving_card = await get_card_by_number(db, receiving_card_number)

    sender_balance = sending_card.balance
    receiver_balance = receiving_card.balance

    if sender_balance.amount < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    sender_balance.amount -= amount
    receiver_balance.amount += amount

    db.add(sender_balance)
    db.add(receiver_balance)

    default_category = await get_category_by_name(db, "User Transfer")
    if not default_category:
        raise HTTPException(status_code=500, detail="Default category for user transfers not found")
    is_internal_transfer = sending_card.balance.user_id == receiving_card.balance.user_id

    transaction = Transaction(
        sender_id=sender_balance.user_id,
        receiver_id=receiver_balance.user_id,
        currency_id=sender_balance.currency_id,
        category_id=default_category.id,
        amount=amount,
        status="completed",
        is_recurring=False,
        created_date=date.today(),
        description=description,
        sender_card_id=sending_card.id,
        receiver_card_id=receiving_card.id,
        transaction_type=TransactionType.USER_TO_USER,
        is_internal_transfer= is_internal_transfer
    )

    db.add(transaction)
    await db.commit()
    return transaction



# async def create_user_to_user_transaction(db: AsyncSession, sender_id: UUID, transaction_data: TransactionCreate):
#     receiver = await db.scalar(select(User).where(User.username == transaction_data.receiver_username))
#     if receiver is None:
#         raise HTTPException(status_code=404, detail="Recipient not found")
    
#     if receiver.id == sender_id:
#         raise HTTPException(status_code=400, detail="Cannot send money to yourself")

#     stmt_sender = select(Balance).where(
#         Balance.user_id == sender_id,
#         Balance.currency_id == transaction_data.currency_id
#     )
#     result = await db.execute(stmt_sender)
#     sender_balance = result.scalar_one_or_none()

#     if not sender_balance:
#         raise HTTPException(status_code=400, detail="Sender does not have a balance in this currency")
    
#     if sender_balance.amount < transaction_data.amount:
#         raise HTTPException(status_code=400, detail="Not enough funds")
    
#     stmt_receiver = select(Balance).where(
#         Balance.user_id == receiver.id,
#         Balance.currency_id == transaction_data.currency_id
#     )
    
#     result = await db.execute(stmt_receiver)
#     receiver_balance = result.scalar_one_or_none()

#     if not receiver_balance:
#         receiver_balance = Balance(
#             user_id=receiver.id,
#             currency_id=transaction_data.currency_id,
#             amount=Decimal("0.0")
#         )
#         db.add(receiver_balance)
#         await db.flush()
        
#     if transaction_data.is_recurring:
#         interval_type = IntervalType.get_interval_type_from_days(transaction_data.interval_days)
#         recurring = RecurringTransaction(
#             sender_id=sender_id,
#             receiver_id=receiver.id,
#             amount=transaction_data.amount,
#             currency_id=transaction_data.currency_id,
#             interval_type=interval_type,
#             next_execution_date=transaction_data.next_run_date or date.today(),
#             description=transaction_data.description,
#             is_active=True,
#             last_run_date=None
#         )
#         db.add(recurring)

#     if transaction_data.category_id is None and transaction_data.category_name:
#         category = await db.scalar(select(Category).where(Category.name == transaction_data.category_name))
#         if not category:
#             category = await create_category(db,sender_id,CategoryCreate(name=transaction_data.category_name,user_id=sender_id ))
#         transaction_data.category_id = category.id
#     elif transaction_data.category_id is None:
#         raise HTTPException(status_code=400, detail="Category must be specified (ID or name)")

#     transaction = Transaction(
#         sender_id=sender_id,
#         receiver_id=receiver.id,
#         currency_id=transaction_data.currency_id,
#         category_id=transaction_data.category_id,
#         amount=transaction_data.amount,
#         status="pending",
#         is_recurring=transaction_data.is_recurring,
#         created_date=date.today(),
#         description=transaction_data.description
#     )
    
#     db.add(transaction)
    
#     await db.commit()
#     await db.refresh(transaction)

#     return transaction