from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.exceptions import CURRENCY_NOT_FOUND

from app.persistence.currencies.currency import Currency


async def _get_currency_id_by_currency_code(
    db: AsyncSession,
    currency_code: str
) -> UUID:
    result = await db.execute(
        select(Currency.id)
        .where(Currency.code == currency_code)
    )
    currency_id = result.scalars().first()
    if not currency_id:
        raise CURRENCY_NOT_FOUND
    return currency_id

async def _get_currency_code_by_currency_id(
    db: AsyncSession,
    currency_id: UUID
) -> UUID:
    result = await db.execute(
        select(Currency.code)
        .where(Currency.id == currency_id)
    )
    currency_code = result.scalars().first()
    if not currency_code:
        raise CURRENCY_NOT_FOUND
    return currency_code