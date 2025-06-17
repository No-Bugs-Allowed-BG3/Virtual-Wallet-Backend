from decimal import Decimal
from uuid import UUID
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.users.users import User
from app.schemas.balance import BalanceResponse,BalanceRequest
from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.card import CardCreate, CardResponse
from app.schemas.user import UserResponse
from app.services.cards_service import create_card, delete_card, load_balance_from_card, read_cards, _card_is_expired

router = APIRouter(prefix="/users/me/cards", tags=["cards"])


@router.post(
    "",
    response_model=CardResponse
)
async def register_card(
    card_in: CardCreate,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Any:
    return await create_card(session, current_user.id, card_in)

@router.delete(
    "/{card_id}"
)
async def remove_card(
    card_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await delete_card(session, current_user.id, card_id)

@router.get(
    "/"
)
async def get_cards(
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[CardResponse]:
    return await read_cards(session, current_user.id)

@router.get("/{card_id}/is_expired")
async def is_card_expired(card_id: UUID, current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session), ) -> bool:
    return await _card_is_expired(session, current_user.id, card_id)

@router.post("/cards/load/")
async def load_balance(
    req:BalanceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    success = await load_balance_from_card(
        db=db,
        user_id=current_user.id,
        expiry=req.expiry,
        cvv_code=req.cvv_code,
        card_number=req.card_number,
        amount=req.amount,
        currency=req.currency_code
    )
    if success:
        return {"detail": "Balance loaded successfully."}
    raise HTTPException(status_code=400, detail="Failed to load balance from card.")