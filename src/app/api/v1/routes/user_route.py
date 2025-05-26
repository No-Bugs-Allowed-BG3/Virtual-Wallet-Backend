from typing import Any,Annotated
from fastapi import APIRouter, Depends,UploadFile,File
from api.exceptions import USER_UNAUTHORIZED,USER_ACTIVATION_ERROR,USER_VERIFICATION_ERROR,USER_ALREADY_EXISTS_EXCEPTION
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.db import get_session
from app.schemas.user import UserResponse, UserCreate,UserSettings
from app.services.users_service import (create_user,
                                        activate_user,
                                        verify_user,
                                        update_user_settings,
                                        update_user_settings_avatar,
                                        get_user_settings)
from app.core.auth.token_functions import (get_current_user,
                                           user_can_interact,
                                           user_can_make_transactions)
from app.schemas.service_result import ServiceResult
from app.schemas.user import UserSettingsResponse
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.card import CardCreate, CardResponse
from app.services.cards_service import create_card
from app.api.deps import get_current_user, SessionDep, CurrentUser

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
                        session:AsyncSession=Depends(get_session))->ServiceResult:
    activation_result = await activate_user(session=session,
                               current_user=current_user)
    if not isinstance(activation_result,ServiceResult):
        raise USER_ACTIVATION_ERROR
    return activation_result

@router.post("/verifications/")
async def _verify_user(current_user:Annotated[UserResponse,Depends(get_current_user)],
                       id_document:Annotated[UploadFile,File()],
                       selfie:Annotated[UploadFile,File()],
                       session: AsyncSession = Depends(get_session))->ServiceResult:
    verification_result = await verify_user(current_user=current_user,
                             id_document=await id_document.read(),
                             selfie=await selfie.read(),
                             session=session)
    if not isinstance(verification_result,ServiceResult):
        raise USER_VERIFICATION_ERROR
    return verification_result

@router.get("/current/settings/")
async def _get_user_settings(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                session: AsyncSession = Depends(get_session))->UserSettingsResponse:
    get_settings_result = await get_user_settings(current_user=current_user,
                                                  session=session)
    if not isinstance(get_settings_result,UserSettingsResponse):
        raise USER_UNAUTHORIZED
    return get_settings_result

@router.post("/current/settings/")
async def _update_user_settings(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                user_settings:UserSettings,
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_result = await update_user_settings(current_user=current_user,
                                                        session=session,
                                                        settings=user_settings)
    if not isinstance(update_settings_result,ServiceResult):
        raise USER_UNAUTHORIZED
    return update_settings_result

@router.post("/current/settings/avatar/")

async def _update_user_settings_avatar(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                avatar:Annotated[UploadFile|None,File()] = None,
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_result = await update_user_settings_avatar(current_user=current_user,
                                                        session=session,
                                                        avatar=avatar.file.read())
    if not isinstance(update_settings_result,ServiceResult):
        raise USER_UNAUTHORIZED
    return update_settings_result
router = APIRouter(prefix="/users/me", tags=["cards"])

@router.post(
    "/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED
)
async def post_card(
    card: CardCreate,
    session: SessionDep,
    current: CurrentUser = Depends(get_current_user),
):
    try:
        # current.id is a uuid.UUID
        return await create_card(
            session=session,
            user_id=current.id,
            card=card
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(ve)
        )
