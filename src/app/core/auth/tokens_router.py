from app.core.auth.token_model import TokenResponse
from app.persistence.users.users import User
from fastapi import APIRouter,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/tokens")

@router.post("/")
async def _login_user(login_data:Annotated[OAuth2PasswordRequestForm,Depends()])->TokenResponse:
    pass
