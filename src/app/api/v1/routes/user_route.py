import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.db import get_session
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
async def reads_user(user: UserCreate) -> Any:
    return await users_service.create_user(user=user)

@router.post("/registrations/")
async def _registers_user(user:UserCreate,session:AsyncSession=Depends(get_session)) -> Any:
    return await users_service.create_user(user=user,session=session)
