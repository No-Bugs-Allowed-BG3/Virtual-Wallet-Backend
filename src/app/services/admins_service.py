from typing import List
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


async def read_transactions(
    db: AsyncSession
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

    result = await db.execute(stmt)
    transactions  = result.scalars().all()

    if not transactions:
        raise TransactionNotFound()

    return transactions

async def block_user(
        db: AsyncSession,
        user_id: UUID
) -> UserBlocked:
    result = await _get_user_by_id(db, user_id)
    user_obj = result.scalar_one()
    user_obj.is_blocked = True
    await db.commit()
    return UserBlocked()

async def unblock_user(
        db: AsyncSession,
        user_id: UUID
) -> UserUnblocked:
    result = await _get_user_by_id(db, user_id)
    user_obj = result.scalar_one()
    user_obj.is_blocked = False
    await db.commit()
    return UserUnblocked()