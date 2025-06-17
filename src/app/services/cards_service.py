from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.exceptions import CardAlreadyExists, NoCards
from app.api.success_responses import CardDeleted
from app.persistence.balances.balance import Balance
from app.schemas.balance import BalanceCreate
from app.services.currencies_service import get_currency_id_by_code
from .balances_service import _get_balance_ids_by_user_id, _get_balance_id_by_user_id_and_currency_code, _create_balance, update_user_balance
from datetime import *
from app.persistence.cards.card import Card
from app.schemas.card import CardCreate, CardResponse
import httpx
from decimal import Decimal

async def create_card(
        db: AsyncSession,
        user_id: UUID,
        card_in: CardCreate
) -> CardResponse:

    balance_id = await _get_balance_id_by_user_id_and_currency_code(
        db, user_id, card_in.currency_code
    )
    currency_id = await get_currency_id_by_code(db, card_in.currency_code.value.upper())
    if not currency_id:
        raise HTTPException(status_code=404, detail="Currency not found")

    if not balance_id:
        balance = await _create_balance(
            db=db,
            user_id=user_id,
            currency_id=currency_id,
            balance_in=BalanceCreate(amount=Decimal("0.00"))
        )
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
    except IntegrityError:
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

    if not cards:
        raise NoCards()

    return [CardResponse.create(c) for c in cards]

async def _card_belongs_to_user(db: AsyncSession, user_id:UUID, card_id:UUID) -> bool:
    balance_ids = await _get_balance_ids_by_user_id(db, user_id)
    result = await db.execute(select(Card)
                              .where(Card.id == card_id)
                              .where(Card.balance_id.in_(balance_ids))
                              .where(Card.is_deleted.is_(False))
                              )
    card = result.scalar_one_or_none()
    return card is not None

async def _card_is_expired(db: AsyncSession, user_id: UUID, card_id: UUID):
    if not await _card_belongs_to_user(db, user_id, card_id):
        raise HTTPException(status_code=403, detail="Card does not belong to user")

    stmt = select(Card).where(Card.id == card_id, Card.expiration_date < datetime.now())
    checked_card = await db.execute(stmt)
    result = checked_card.scalar_one_or_none()
    if result:
        return True
    else:
        return False


async def load_balance_from_card(db: AsyncSession, expiry:str,cvv_code:str,user_id: UUID, card_number:str, amount: str, currency:str):
    payload = {
        "cvv_code": cvv_code,
        "number": card_number,
        "expiry": expiry,
        "currency": currency,
        "requested_amount":str(amount)
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8002/cards/withdrawals/", json=payload)
    print(response.json().get("approved"))
    if response.status_code == 200 and response.json().get("approved") == True:
        await update_user_balance(db, user_id, Decimal(amount), currency)
        return True
    else:
        return False


async def get_card_by_number(db: AsyncSession, card_number: str) -> Card | None:
    result = await db.execute(
        select(Card)
        .options(
            selectinload(Card.balance).selectinload(Balance.user)
        )
        .where(Card.card_number == card_number, Card.is_deleted == False)
    )
    return result.scalar_one_or_none()