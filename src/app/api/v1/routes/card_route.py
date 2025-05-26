from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.card import CardCreate, CardResponse
from app.services.cards_service import create_card
from app.api.deps import get_current_user, SessionDep, CurrentUser

router = APIRouter(prefix="/users/me", tags=["cards"])

@router.post(
    "/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED
)
async def post_card(
    card: CardCreate,
    session: SessionDep,
    current: CurrentUser = Depends(get_current_user),
):
    try:
        # current.id is a uuid.UUID
        return await create_card(
            session=session,
            user_id=current.id,
            card=card
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(ve)
        )