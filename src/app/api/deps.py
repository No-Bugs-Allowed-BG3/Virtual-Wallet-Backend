from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserResponse

oauth2 = OAuth2PasswordBearer(tokenUrl="")


def get_db() -> Generator[AsyncSession, None, None]:
    pass


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> UserResponse:
    pass


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
