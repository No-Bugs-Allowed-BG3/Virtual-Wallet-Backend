from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from sqlalchemy import select
from app.persistence.transactions.transaction import Transaction
from app.persistence.recurring_transactions.recurring_transaction import RecurringTransaction
from app.persistence.balances.balance import Balance
from app.persistence.users.users import User
from app.schemas.transaction import TransactionCreate
from app.services.users_service import *
from app.schemas.transaction import RecurringTransactionCreate
from app.core.enums.enums import IntervalType

from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal

async def create_user_to_user_transaction(db: AsyncSession, sender_id: UUID, transaction_data: TransactionCreate):
    receiver = await db.scalar(select(User).where(User.username == transaction_data.receiver_username))
    if receiver is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    if receiver.id == sender_id:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")

    stmt_sender = select(Balance).where(
        Balance.user_id == sender_id,
        Balance.currency_id == transaction_data.currency_id
    )
    result = await db.execute(stmt_sender)
    sender_balance = result.scalar_one_or_none()

    if not sender_balance:
        raise HTTPException(status_code=400, detail="Sender does not have a balance in this currency")
    
    if sender_balance.amount < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Not enough funds")
    
    stmt_receiver = select(Balance).where(
        Balance.user_id == receiver.id,
        Balance.currency_id == transaction_data.currency_id
    )
    
    result = await db.execute(stmt_receiver)
    receiver_balance = result.scalar_one_or_none()

    if not receiver_balance:
        receiver_balance = Balance(
            user_id=receiver.id,
            currency_id=transaction_data.currency_id,
            amount=Decimal("0.0")
        )
        db.add(receiver_balance)
        await db.flush()
        
    if transaction_data.is_recurring:
        interval_type = IntervalType.get_interval_type_from_days(transaction_data.interval_days)
        recurring = RecurringTransaction(
            sender_id=sender_id,
            receiver_id=receiver.id,
            amount=transaction_data.amount,
            currency_id=transaction_data.currency_id,
            interval_type=interval_type,
            next_execution_date=transaction_data.next_run_date or date.today(),
            description=transaction_data.description,
            is_active=True,
            last_run_date=None
        )
        db.add(recurring)

    transaction = Transaction(
        sender_id=sender_id,
        receiver_id=receiver.id,
        currency_id=transaction_data.currency_id,
        category_id=transaction_data.category_id,
        amount=transaction_data.amount,
        status="pending",
        is_recurring=transaction_data.is_recurring,
        created_date=date.today(),
        description=transaction_data.description
    )
    
    db.add(transaction)
    sender_balance.amount -= transaction_data.amount
    receiver_balance.amount += transaction_data.amount
    
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