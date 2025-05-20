import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.schemas.user import UserResponse, UserCreate
from app.services import users_service
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_user,
)

router = APIRouter()


@router.post(
    "/",
    # dependencies=[Depends(get_current_user)],
    response_model=UserResponse,
)
async def reads_user(session: SessionDep, user: UserCreate) -> Any:
    return await users_service.create_user(session=session, user=user)
