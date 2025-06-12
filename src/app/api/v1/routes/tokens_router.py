from services.tokens_service import login_user,login_user_device
from app.schemas.user import UserLogin
from app.persistence.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,Form
from fastapi.responses import JSONResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.api.exceptions import UserUnauthorized

token_router = APIRouter()

@token_router.post("/")
async def _login_user(login_data:Annotated[OAuth2PasswordRequestForm,Depends()],session:AsyncSession=Depends(get_session))->JSONResponse:
    usr = UserLogin.from_oauth2_form_data(login_data)
    user_tokens = await login_user(session=session,usr=usr)
    if user_tokens:
        response = JSONResponse(
            content={"result":"success"}
        )
        response.set_cookie(
            key="access_token",
            value=user_tokens.access.access_token,
            expires=user_tokens.access.expiry,
            httponly=True
        )
        response.set_cookie(
            key="refresh_token",
            value=user_tokens.refresh.access_token,
            expires=user_tokens.refresh.expiry,
            httponly=True
        )
    else:
        response = JSONResponse(
            content={"result":"failure"}
        )
    return response

@token_router.post("/device/")
async def _login_user_device(device_id:Annotated[str,Form()],
                             login_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                             session:AsyncSession=Depends(get_session))->JSONResponse:
    usr = UserLogin.from_oauth2_form_data(login_data)
    user_tokens = await login_user_device(session=session,usr=usr,device_id=device_id)
    if user_tokens:
        response = JSONResponse(
            content={"result":"success"}
        )
        response.set_cookie(
            key="device_token",
            value=user_tokens.access_token,
            expires=user_tokens.expiry,
            httponly=True
        )
    else:
        raise UserUnauthorized()
    return response

