from typing import Any,Annotated

from fastapi import APIRouter, Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.db import get_session
from app.schemas.user import UserResponse, UserCreate
from app.services.users_service import create_user
from app.core.auth.token_functions import get_current_user
from app.api.deps import (
    SessionDep,
)

router = APIRouter()

@router.post("/current/")
async def _get_current_user(current_user:Annotated[UserResponse,Depends(get_current_user)])->UserResponse|bool|dict:
    if not current_user:
        return False
    return current_user

@router.post("/registrations/")
async def _registers_user(user:UserCreate,session:AsyncSession=Depends(get_session)) -> Any:
    return await create_user(user=user,session=session)
