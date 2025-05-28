from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.exceptions import CARD_ALREADY_EXISTS, CARD_NOT_FOUND
from .balances_service import _get_balance_ids_by_user_id, _get_balance_id_by_user_id_and_currency_code, _create_balance

from app.persistence.cards.card import Card
from app.schemas.card import CardCreate, CardResponse

async def create_card(
    db: AsyncSession,
    user_id: UUID,
    card_in: CardCreate,
    currency_code: str
) -> CardResponse:
    balance_id = await _get_balance_id_by_user_id_and_currency_code(db, user_id, currency_code)
    if not balance_id:
        balance = await _create_balance(db, user_id, currency_code)
        balance_id = await balance.id
    card = Card(balance_id=balance_id, **card_in.model_dump())
    db.add(card)
    try:
        await db.flush()
        await db.commit()
        await db.refresh(card)
    except IntegrityError:
        await db.rollback()
        raise CARD_ALREADY_EXISTS
    return CardResponse.create(card)

async def delete_card(
        db: AsyncSession,
        balance_id: UUID,
        card_id: UUID
) -> None:
    card = await db.get(Card, card_id)
    if not card or card.balance_id != balance_id or card.is_deleted:
        raise CARD_NOT_FOUND
    card.is_deleted = True
    try:
        await db.commit()
    except:
        await db.rollback()

async def read_cards(
        db: AsyncSession,
        user_id: UUID
) -> List[CardResponse]:
    balance_ids = await _get_balance_ids_by_user_id(db, user_id)

    result = await db.execute(
        select(Card)
        .where(
            Card.balance_id.in_(balance_ids),
            Card.is_deleted.is_(False)
        )
    )

    cards = result.scalars().all()

    return [CardResponse.create(c) for c in cards]