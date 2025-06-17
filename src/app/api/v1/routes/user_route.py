from typing import Any,Annotated
from fastapi import APIRouter,Depends,UploadFile,File,Form
from app.schemas.confirmation import ConfirmationResponse,ConfirmationItem
from api.exceptions import UserUnauthorized,UserAlreadyExists,UserNotFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.db import get_session
from app.services.errors import ServiceError
from app.schemas.user import (UserResponse,
                              UserCreate,
                              UserSettings,
                              UserPasswordCollection,
                              UserSettingsResponse,
                              UserContactResponse)
from app.services.users_service import (create_user,
                                        activate_user,
                                        verify_user,
                                        update_user_settings_contacts,
                                        update_user_settings_avatar,
                                        update_user_settings_password,
                                        get_user_settings,
                                        _get_user_info_by_username,
                                        get_actions_for_confirmation,
                                        confirm_user_financial_action,
                                        update_user_settings_pin,
                                        get_transaction_status)
from services.utils.token_functions import (get_current_user,
                                            get_current_user_device,
                                            user_can_interact,
                                            user_can_make_transactions)
from app.schemas.service_result import ServiceResult

router = APIRouter()

@router.post("/current/")
async def _get_current_user(current_user:Annotated[UserResponse,Depends(get_current_user)])->UserResponse|bool|dict:
    if not current_user:
        raise UserUnauthorized()
    return current_user

@router.post("/current/interactions/")
async def _get_interaction_rights(interaction_rights:Annotated[ServiceResult,Depends(user_can_interact)])->ServiceResult:
    return interaction_rights

@router.post("/current/transactions/")
async def _get_interaction_rights(transaction_rights:Annotated[bool,Depends(user_can_make_transactions)])->bool|dict:
    return transaction_rights

@router.post("/registrations/")
async def _registers_user(user:UserCreate,session:AsyncSession=Depends(get_session)) -> Any:
    creation_result = await create_user(user=user,session=session)
    if not isinstance(creation_result,UserResponse):
        raise UserAlreadyExists()
    return creation_result


@router.get("/activations/")
async def _activate_user(current_user:Annotated[UserResponse,Depends(get_current_user)],
                        session:AsyncSession=Depends(get_session))->ServiceResult:
    activation_result = await activate_user(session=session,
                               current_user=current_user)
    if not isinstance(activation_result,ServiceResult):
        raise UserUnauthorized()
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
        raise UserUnauthorized()
    return verification_result

@router.get("/current/settings/")
async def _get_user_settings(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                session: AsyncSession = Depends(get_session))->UserSettingsResponse:
    get_settings_result = await get_user_settings(current_user=current_user,
                                                  session=session)
    if not isinstance(get_settings_result,UserSettingsResponse):
        raise UserUnauthorized()
    return get_settings_result

@router.post("/current/settings/contacts/")
async def _update_user_settings_contacts(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                user_settings:UserSettings,
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_contacts_result = await update_user_settings_contacts(current_user=current_user,
                                                        session=session,
                                                        settings=user_settings)
    if not isinstance(update_settings_contacts_result,ServiceResult):
        raise UserUnauthorized()
    return update_settings_contacts_result

@router.post("/current/settings/pin/")
async def _update_user_settings_contacts(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                user_pin:Annotated[str,Form()],
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_pin = await update_user_settings_pin(current_user=current_user,
                                                        session=session,
                                                        user_pin=user_pin)
    if not isinstance(update_settings_pin,ServiceResult):
        raise UserUnauthorized()
    return update_settings_pin


@router.post("/current/settings/password/")
async def _update_user_settings_password(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                password_collection:UserPasswordCollection,
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_password_result = await update_user_settings_password(current_user=current_user,
                                    session=session,
                                    old_password=password_collection.old_password,
                                    new_password=password_collection.new_password
                                    )
    if not isinstance(update_settings_password_result,ServiceResult):
        raise UserUnauthorized()
    return update_settings_password_result

@router.post("/current/settings/avatar/")
async def _update_user_settings_avatar(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                avatar:Annotated[UploadFile|None,File()] = None,
                                session: AsyncSession = Depends(get_session))->ServiceResult:
    update_settings_result = await update_user_settings_avatar(current_user=current_user,
                                                        session=session,
                                                        avatar=avatar.file.read())
    if not isinstance(update_settings_result,ServiceResult):
        raise UserUnauthorized()
    return update_settings_result

@router.get("/others/{username}/")
async def get_user_info_by_username(current_user:Annotated[UserResponse,Depends(get_current_user)],
                                    username:str,
                                    session: AsyncSession = Depends(get_session)):
    user_info:UserContactResponse = await _get_user_info_by_username(db=session,
                                                                     username=username)
    if not isinstance(user_info,UserContactResponse):
        raise UserUnauthorized()
    return user_info

@router.post("/confirmations/")
async def _user_confirm_action(confirmation_target:Annotated[str,Form()],
                               confirmation_target_id:Annotated[str,Form()],
                               user_pin:Annotated[str,Form()],
                               current_user:Annotated[UserResponse,Depends(get_current_user_device)],
                               session:AsyncSession = Depends(get_session))->ConfirmationResponse:
    confirm_user_financial_action_result = await confirm_user_financial_action(current_user=current_user,
                                                session=session,
                                                confirmation_target=confirmation_target,
                                                confirmation_target_id=confirmation_target_id,
                                                user_pin=user_pin)
    print(confirm_user_financial_action_result)
    if not isinstance(confirm_user_financial_action_result,ConfirmationResponse):
        raise UserUnauthorized
    return confirm_user_financial_action_result

@router.post("/confirmations/all/")
async def _user_confirm_action(current_user:Annotated[UserResponse,Depends(get_current_user_device)],
                               session:AsyncSession = Depends(get_session))->ConfirmationItem|ServiceResult:
    actions_for_confirmation = await get_actions_for_confirmation(current_user=current_user,
                                                session=session)
    if isinstance(actions_for_confirmation,ConfirmationItem):
        return actions_for_confirmation
    if isinstance(actions_for_confirmation,ServiceError):
        return ServiceResult(result=False)
    raise UserUnauthorized

@router.post("/confirmations/check/{transaction_id}/")
async def _user_check_transaction(transaction_id:str,
                                  current_user:Annotated[UserResponse,Depends(get_current_user)],
                               session:AsyncSession = Depends(get_session))->ServiceError|ServiceResult:
    transaction_status = await get_transaction_status(current_user=current_user,
                                                session=session,
                                                transaction_id=transaction_id)
    if isinstance(transaction_status,ServiceError):
        return ServiceResult(result=False)
    return transaction_status

@router.post("/current/device/")
async def _user_confirm_action(current_user:Annotated[UserResponse,Depends(get_current_user_device)])\
        ->ServiceResult:
    if not current_user:
        return ServiceResult(result=False)
    else:
        return ServiceResult(result=True)