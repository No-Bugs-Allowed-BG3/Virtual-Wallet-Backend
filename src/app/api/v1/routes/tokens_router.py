from app.services.tokens_service import login_user
from app.schemas.user import UserLogin
from app.persistence.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

token_router = APIRouter()


##@token_router.post("/")
#async def _login_user(
    #login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    #session: AsyncSession = Depends(get_session),
#) -> JSONResponse:
    #usr = UserLogin.from_oauth2_form_data(login_data)
    #user_tokens = await login_user(session=session, usr=usr)
    #if user_tokens:
        #response = JSONResponse(content={"result": "success"})
        #response.set_cookie(
            #key="access_token",
            #value=user_tokens.access.access_token,
            #expires=user_tokens.access.expiry,
            #httponly=True,
        #)
        #response.set_cookie(
            #key="refresh_token",
            #value=user_tokens.refresh.access_token,
            #expires=user_tokens.refresh.expiry,
            #httponly=True,
        #)
    #else:
        #response = JSONResponse(content={"result": "failure"})
    #return response

@token_router.post("/")
async def _login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    usr = UserLogin.from_oauth2_form_data(login_data)
    user_tokens = await login_user(session=session, usr=usr)
    
    if user_tokens:
        response = JSONResponse(content={
            "result": "success",
        })
        response.set_cookie(
            key="access_token",
            value=user_tokens.access.access_token,
            expires=user_tokens.access.expiry,
            httponly=True,
        )
        response.set_cookie(
            key="refresh_token",
            value=user_tokens.refresh.access_token,
            expires=user_tokens.refresh.expiry,
            httponly=True,
        )
    else:
        response = JSONResponse(content={"result": "failure"})
    
    return response
