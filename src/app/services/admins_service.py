from typing import List

from fastapi import HTTPException
from app.api.exceptions import TransactionNotFound, UserNotFound
from app.api.success_responses import UserBlocked, UserUnblocked
from app.persistence.categories.categories import Category
from app.persistence.users.users import User
from app.persistence.transactions.transaction import Transaction
from app.persistence.currencies.currency import Currency
from app.schemas.transaction import AdminTransactionResponse
from app.schemas.user import AdminUserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import UUID, select
from sqlalchemy.orm import aliased

from app.services.users_service import _get_user_by_id


async def read_users(
        db: AsyncSession
) -> List[AdminUserResponse]:
    stmt   = select(User)
    result = await db.execute(stmt)
    users  = result.scalars().all()

    if not users:
        raise UserNotFound()

    return users


from datetime import date
from uuid import UUID
from typing import List

async def read_transactions(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
    sender_username: str | None = None,
    receiver_username: str | None = None,
    direction: str | None = None,
    user_id: UUID | None = None,
    limit: int = 20,
    offset: int = 0,
) -> List[AdminTransactionResponse]:


    Sender = aliased(User)
    Receiver = aliased(User)

    stmt = (
        select(
            Transaction.id.label("id"),
            Sender.username.label("sender_username"),
            Currency.code.label("currency_code"),
            Receiver.username.label("receiver_username"),
            Category.name.label("category_name"),
            Transaction.amount.label("amount"),
            Transaction.status.label("status"),
            Transaction.is_recurring.label("is_recurring"),
            Transaction.created_date.label("created_date"),
        )
        .join(Sender,   Transaction.sender_id   == Sender.id)
        .join(Receiver, Transaction.receiver_id == Receiver.id)
        .join(Currency,  Transaction.currency_id == Currency.id)
        .join(Category,  Transaction.category_id == Category.id)
    )

    if start_date:
        stmt = stmt.where(Transaction.created_date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.created_date <= end_date)
    if sender_username:
        stmt = stmt.where(Sender.username == sender_username)
    if receiver_username:
        stmt = stmt.where(Receiver.username == receiver_username)

    if direction and user_id:
        if direction == "incoming":
            stmt = stmt.where(Transaction.receiver_id == user_id)
        elif direction == "outgoing":
            stmt = stmt.where(Transaction.sender_id == user_id)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    rows = result.all()
    transactions = [AdminTransactionResponse(**dict(row)) for row in rows]

    if not transactions:
        raise TransactionNotFound()

    return transactions

async def block_user(
        db: AsyncSession,
        user_id: UUID
) -> UserBlocked:
    user_obj = await _get_user_by_id(db, user_id)
    user_obj.is_blocked = True
    await db.commit()
    return UserBlocked()

async def unblock_user(
        db: AsyncSession,
        user_id: UUID
) -> UserUnblocked:
    user_obj = await _get_user_by_id(db, user_id)
    user_obj.is_blocked = False
    await db.commit()
    return UserUnblocked()

async def get_transaction_by_id(db: AsyncSession, transaction_id: UUID) -> Transaction:
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction