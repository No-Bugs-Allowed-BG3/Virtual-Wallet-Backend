from typing import Any,Annotated

from fastapi import APIRouter, Depends,UploadFile,File
from api.exceptions import USER_UNAUTHORIZED,USER_ACTIVATION_ERROR,USER_VERIFICATION_ERROR,USER_ALREADY_EXISTS_EXCEPTION
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.db import get_session
from app.schemas.user import UserResponse, UserCreate
from app.services.users_service import create_user,activate_user,verify_user
from app.core.auth.token_functions import (get_current_user,
                                           user_can_interact,
                                           user_can_make_transactions)

router = APIRouter()

@router.post("/current/")
async def _get_current_user(current_user:Annotated[UserResponse,Depends(get_current_user)])->UserResponse|bool|dict:
    if not current_user:
        raise USER_UNAUTHORIZED
    return current_user

@router.post("/current/interactions/")
async def _get_interaction_rights(interaction_rights:Annotated[bool,Depends(user_can_interact)])->bool|dict:
    return interaction_rights

@router.post("/current/transactions/")
async def _get_interaction_rights(transaction_rights:Annotated[bool,Depends(user_can_make_transactions)])->bool|dict:
    return transaction_rights

@router.post("/registrations/")
async def _registers_user(user:UserCreate,session:AsyncSession=Depends(get_session)) -> Any:
    creation_result = await create_user(user=user,session=session)
    if not isinstance(creation_result,UserResponse):
        raise USER_ALREADY_EXISTS_EXCEPTION
    return creation_result


@router.get("/activations/")
async def _activate_user(current_user:Annotated[UserResponse,Depends(get_current_user)],
                        session:AsyncSession=Depends(get_session))->bool:
    activation_result = await activate_user(session=session,
                               current_user=current_user)
    if not isinstance(activation_result,bool):
        raise USER_ACTIVATION_ERROR
    return activation_result

@router.post("/verifications/")
async def _verify_user(current_user:Annotated[UserResponse,Depends(get_current_user)],
                       id_document:Annotated[UploadFile,File()],
                       selfie:Annotated[UploadFile,File()],
                       session: AsyncSession = Depends(get_session))->bool:
    verification_result = await verify_user(current_user=current_user,
                             id_document=await id_document.read(),
                             selfie=await selfie.read(),
                             session=session)
    if not isinstance(verification_result,bool):
        raise USER_VERIFICATION_ERROR
    return verification_result