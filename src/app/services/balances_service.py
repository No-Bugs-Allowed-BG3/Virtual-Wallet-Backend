from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.api.exceptions import BalanceAlreadyExists, BalanceNotFound
from app.schemas.balance import BalanceResponse
from app.persistence.balances.balance import Balance
from .currencies_service import _get_currency_id_by_currency_code

async def _create_balance(
        db: AsyncSession,
        user_id: UUID,
        currency_code: str     
) -> BalanceResponse:
    currency_id = await _get_currency_id_by_currency_code(db, currency_code)
    balance = Balance(user_id=user_id,currency_id=currency_id)
    db.add(balance)
    try:
        await db.flush()
        await db.commit()
        await db.refresh(balance)
    except IntegrityError:
        await db.rollback()
        raise BalanceAlreadyExists()
    return BalanceResponse(
        id=balance.id,
        amount=balance.amount,
        currency_code=currency_code,
    )

async def _get_balance_ids_by_user_id(
    db: AsyncSession,
    user_id: UUID
) -> List[UUID]:
    result = await db.execute(
        select(Balance.id)
        .where(Balance.user_id == user_id)
    )
    balance_ids = result.scalars().all()
    if not balance_ids:
        raise BalanceNotFound()
    return balance_ids

async def _get_balance_id_by_user_id_and_currency_code(
        db: AsyncSession,
        user_id: UUID,
        currency_code: str 
) -> UUID:
    currency_id = await _get_currency_id_by_currency_code(db, currency_code)
    result = await db.execute(
        select(Balance.id)
        .where(
            Balance.user_id == user_id,
            Balance.currency_id == currency_id
            )
    )
    balance_id = result.scalars().first()
    return balance_id