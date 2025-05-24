import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.schemas.card import CardResponse, CardCreate
from app.services import cards_service
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_user,
)

router = APIRouter(prefix="/users/me", tags=["cards"])


@router.post("/cards",
    dependencies=[Depends(get_current_user)],
    response_model=CardResponse,
)
async def post_card(session: SessionDep, card: CardCreate) -> Any:
    return await cards_service.create_card(session=session, card=card)
