from uuid import UUID
from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.card import CardCreate, CardResponse
from app.schemas.user import UserResponse
from app.services.cards_service import create_card, delete_card, read_cards, check_if_card_is_expired

router = APIRouter(prefix="/users/me/cards", tags=["cards"])


@router.post(
    "/",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_card(
    card_in: CardCreate,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Any:
    return await create_card(session, current_user.id, card_in)

@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_card(
    card_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await delete_card(session, current_user.id, card_id)

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_cards(
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[CardResponse]:
    return await read_cards(session, current_user.id)

@router.get("/{card_id}/is_expired")
async def is_card_expired(card_id: UUID, current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_session), ) -> bool:
    return await check_if_card_is_expired(session, current_user.id, card_id)