from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import CardAlreadyExists
from app.api.success_responses import CardDeleted
from .balances_service import _get_balance_ids_by_user_id, _get_balance_id_by_user_id_and_currency_code, _create_balance

from app.persistence.cards.card import Card
from app.schemas.card import CardCreate, CardResponse

async def create_card(
    db: AsyncSession,
    user_id: UUID,
    card_in: CardCreate
) -> CardResponse:
    balance_id = await _get_balance_id_by_user_id_and_currency_code(db, user_id, card_in.currency_code)
    if not balance_id:
        balance = await _create_balance(db, user_id, card_in.currency_code)
        balance_id = balance.id
    card = Card(
        balance_id=balance_id, 
        card_number=card_in.card_number, 
        expiration_date=card_in.expiration_date,
        cardholder_name=card_in.cardholder_name,
        cvv=card_in.cvv,
        )
    db.add(card)
    try:
        await db.flush()
        await db.refresh(card)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise CardAlreadyExists()
    return CardResponse.create(card)

async def delete_card(
        db: AsyncSession,
        user_id: UUID,
        card_id: UUID
) -> None:
    balance_ids = await _get_balance_ids_by_user_id(db, user_id)
    result = await db.execute(
        select(Card)
        .where(
            Card.id == card_id,
            Card.balance_id.in_(balance_ids),
            Card.is_deleted.is_(False)
        )
    )
    card = result.scalar_one()
    card.is_deleted = True
    await db.commit()
    return CardDeleted()

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