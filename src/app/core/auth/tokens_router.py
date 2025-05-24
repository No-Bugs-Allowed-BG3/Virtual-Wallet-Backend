from app.core.auth.token_model import TokenCollection
from app.core.auth.tokens_service import login_user
from app.schemas.user import UserLogin
from app.persistence.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

token_router = APIRouter()

@token_router.post("/")
async def _login_user(login_data:Annotated[OAuth2PasswordRequestForm,Depends()],session:AsyncSession=Depends(get_session))->TokenCollection:
    usr = UserLogin.from_oauth2_form_data(login_data)
    return await login_user(session=session,usr=usr)
