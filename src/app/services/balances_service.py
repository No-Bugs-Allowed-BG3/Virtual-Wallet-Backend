from decimal import Decimal
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.api.exceptions import BALANCE_ALREADY_EXISTS
from app.schemas.balance import BalanceResponse, BalanceCreate
from app.api.exceptions import BalanceNotFound
from app.schemas.balance import BalanceResponse
from app.persistence.balances.balance import Balance
from .currencies_service import _get_currency_id_by_currency_code

async def _create_balance(
    db: AsyncSession,
    user_id: UUID,
    currency_id: UUID,
    balance_in: BalanceCreate
) -> BalanceResponse:
    balance = Balance(
        user_id=user_id,
        currency_id=currency_id,
        amount=balance_in.amount,
    )
    db.add(balance)
    try:
        await db.flush()
        await db.refresh(balance, attribute_names=["currency"])
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise BALANCE_ALREADY_EXISTS

    return BalanceResponse(
        id=balance.id,
        amount=balance.amount,
        currency_code=balance.currency.code,
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

async def get_balance_by_user_and_currency(db: AsyncSession,user_id: UUID,currency_code: str) -> Balance | None:
    currency_id = await _get_currency_id_by_currency_code(db, currency_code)

    result = await db.execute(
        select(Balance)
        .where(
            Balance.user_id == user_id,
            Balance.currency_id == currency_id
        )
    )
    return result.scalars().first()

async def update_user_balance(db: AsyncSession,user_id: UUID,amount: Decimal,currency: str):
    balance = await get_balance_by_user_and_currency(db, user_id, currency)

    if balance:
        balance.amount += amount
    else:
        currency_id = await _get_currency_id_by_currency_code(db, currency)
        balance = Balance(
            user_id=user_id,
            currency_id=currency_id,
            amount=amount
        )
        db.add(balance)

    await db.commit()
    return balance