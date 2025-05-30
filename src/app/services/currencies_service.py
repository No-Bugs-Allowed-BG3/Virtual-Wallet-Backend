from typing import Union
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.exceptions import CurrencyNotFound

from app.core.enums.enums import AvailableCurrency
from app.persistence.currencies.currency import Currency


async def _get_currency_id_by_currency_code(
    db: AsyncSession,
    currency_code: Union[str, AvailableCurrency]
) -> UUID:
    
    if isinstance(currency_code, AvailableCurrency):
        code = currency_code.value
    else:
        code = currency_code

    # 2) normalize (strip + lowercase)
    code = code.strip().upper()
    
    result = await db.execute(
        select(Currency.id)
        .where(Currency.code == code)
    )
    currency_id = result.scalars().first()
    if not currency_id:
        raise CurrencyNotFound()
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
        raise CurrencyNotFound()
    return currency_code