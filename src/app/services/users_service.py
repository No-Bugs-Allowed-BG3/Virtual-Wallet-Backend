from app.api.exceptions import UserNotFound
from app.persistence.users.users import User
from uuid import UUID
from app.schemas.user import UserCreate, UserResponse,UserSettings,UserSettingsResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from sqlalchemy import update, select
from app.services.utils.security import get_password_hash,verify_password
from app.services.utils.processors import process_db_transaction
from app.services.utils.mail.sendmail import send_activation_mail
from app.services.errors import ServiceError
import requests
from os import getenv
import cloudinary
import cloudinary.uploader
from app.schemas.service_result import ServiceResult
from app.schemas.confirmation import (ConfirmationResponse,
                                      TargetEnum,
                                      ConfirmationItem)
from app.persistence.transactions.transaction import Transaction

async def create_user(session:AsyncSession ,user: UserCreate) -> UserResponse|ServiceError:
    async def _create():
        user.password = get_password_hash(user.password)
        db_obj = User(**user.model_dump())
        session.add(db_obj)
        try:
            await session.commit()
        except IntegrityError:
            return ServiceError.ERROR_USER_EXISTS
        await session.refresh(db_obj)
        await send_activation_mail(to_email=str(user.email),
                                   to_username=user.username,
                                   to_user_id=str(db_obj.id))
        return UserResponse.create(db_obj)

    return await process_db_transaction(
        session=session,
        transaction_func=_create,
    )

async def activate_user(current_user:UserResponse,
                        session:AsyncSession) -> ServiceResult|ServiceError:
    async def _activate():
        statement = update(User).where(User.id == current_user.id).values(is_activated=True)
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND
    service_result = await process_db_transaction(
        session=session,
        transaction_func=_activate,
    )
    return ServiceResult(
        result=service_result
    )

async def verify_user(current_user:UserResponse,
                 id_document:bytes,
                 selfie:bytes,
                 session:AsyncSession)->ServiceResult|ServiceError:
    files = {"id_document":id_document,
             "selfie":selfie}
    verification_result = bool(requests.post(
        url=getenv("VERIFICATION_API_URL"),
        files=files
    ))
    if verification_result:
        statement = update(User).where(User.id == current_user.id).values(is_verified=True)
        result = await session.execute(statement)
        await session.commit()
        if not result.rowcount:
            return ServiceError.ERROR_USER_NOT_FOUND

    return ServiceResult(
        result=verification_result
    )

async def update_user_settings_avatar(current_user:UserResponse,
                               session:AsyncSession,
                               avatar:bytes|None)->ServiceResult|ServiceError:
    async def _update_avatar():
        if avatar:
            cloudinary.config(
                cloud_name=getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=getenv("CLOUDINARY_API_KEY"),
                api_secret=getenv("CLOUDINARY_SECRET_KEY"),
                secure=True
            )
            upload_result = cloudinary.uploader.upload(avatar)
            avatar_full_location = upload_result["secure_url"]
        else:
            avatar_full_location = None

        statement = update(User).where(User.id == current_user.id).values(
            avatar=avatar_full_location
        )
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND

    service_result = await process_db_transaction(
        session=session,
        transaction_func=_update_avatar,
    )
    return ServiceResult(
        result=service_result
    )


async def update_user_settings_contacts(current_user:UserResponse,
                               session:AsyncSession,
                               settings:UserSettings) -> ServiceResult|ServiceError:
    async def _get_old_user_info():
        statement = select(User).where(User.id == current_user.id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        return user_object

    old_user_info = await _get_old_user_info()
    old_user_email = str(old_user_info.email)
    emails_differ = not (settings.email == old_user_email)
    async def _update_settings():
        if not emails_differ:
            statement = update(User).where(User.id == current_user.id).values(
                email=settings.email,
                phone=settings.phone
                )
        else:
            statement = update(User).where(User.id == current_user.id).values(
                email=settings.email,
                phone=settings.phone,
                is_activated=False
                )
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND

    service_result = await process_db_transaction(
        session=session,
        transaction_func=_update_settings,
    )
    if emails_differ and service_result:
        await send_activation_mail(
            to_user_id=str(old_user_info.id),
            to_email=str(settings.email),
            to_username=str(old_user_info.username)
        )
    return ServiceResult(
        result=service_result
    )

async def update_user_settings_password(current_user:UserResponse,
                               session:AsyncSession,
                               old_password:str,
                                new_password:str) -> ServiceResult|ServiceError:
    async def _update_settings_password():
        statement = select(User).where(User.id == current_user.id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            return False
        if not verify_password(old_password,user_object.password):
            return False
        new_password_hash = get_password_hash(new_password)
        statement = update(User).where(User.id == current_user.id).values(
            password = new_password_hash
            )
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND

    service_result = await process_db_transaction(
        session=session,
        transaction_func=_update_settings_password,
    )
    return ServiceResult(
        result=service_result
    )

async def update_user_settings_pin(current_user:UserResponse,
                               session:AsyncSession,
                                user_pin:str) -> ServiceResult|ServiceError:
    async def _update_settings_password():
        statement = select(User).where(User.id == current_user.id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            return False
        pin_hash = get_password_hash(user_pin)
        statement = update(User).where(User.id == current_user.id).values(
            user_pin = pin_hash
            )
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND

    service_result = await process_db_transaction(
        session=session,
        transaction_func=_update_settings_password,
    )
    return ServiceResult(
        result=service_result
    )

async def get_user_settings(current_user:UserResponse,
                               session:AsyncSession) -> UserSettingsResponse|ServiceError:
    async def _get_settings():
        statement = select(User).where(User.id == current_user.id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            return ServiceError.ERROR_USER_NOT_FOUND
        return UserSettingsResponse.create(user_object)

    return await process_db_transaction(
        session=session,
        transaction_func=_get_settings,
    )

async def confirm_user_financial_action(current_user:UserResponse,
                                        confirmation_target:str,
                                        confirmation_target_id:str,
                                        user_pin:str,
                                        session:AsyncSession)->ConfirmationResponse|ServiceError:
    async def _confirm_user_action():
        statement = select(User).where(User.id == current_user.id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            return ServiceError.ERROR_USER_NOT_FOUND
        if not verify_password(user_pin,user_object.user_pin):
            return ServiceError.ERROR_USER_INVALID_PIN
        if confirmation_target == TargetEnum.transaction.value:
            statement = update(Transaction).where(Transaction.id == confirmation_target_id).values(is_approved=True)
            result = await session.execute(statement)
            await session.commit()
            if not result.rowcount:
                return ServiceError.ERROR_DURING_CONFIRMATION
            else:
                return ConfirmationResponse(
                    confirmation_result=True,
                    confirmation_target=TargetEnum(confirmation_target),
                    confirmation_target_id=UUID(confirmation_target_id)
                )
    return await process_db_transaction(session=session,
                                        transaction_func=_confirm_user_action)

async def get_actions_for_confirmation(current_user:UserResponse,
                                       session:AsyncSession)-> ConfirmationItem|ServiceError:
    async def _get_confirmation_items():
        statement = select(Transaction).where((Transaction.is_approved==False) &
                                              (Transaction.sender_id == current_user.id)).\
                                            order_by(Transaction.created_date).limit(1)
        result = await session.execute(statement)
        transaction_item = result.scalar_one_or_none()
        if not transaction_item:
            return ServiceError.ERROR_NO_PENDING_CONFIRMATIONS
        statement = select(User).where(User.id == transaction_item.receiver_id)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            return ServiceError.ERROR_NO_PENDING_CONFIRMATIONS
        return ConfirmationItem(
            confirmation_target=TargetEnum.transaction,
            confirmation_target_id=transaction_item.id,
            receiver=user_object.username
            )

    return await process_db_transaction(session=session,
                                        transaction_func=_get_confirmation_items)

async def _get_user_by_id(
        db: AsyncSession,
        user_id: UUID
) -> User:
    result = await db.execute(
        select(User)
        .where(
            User.id == user_id
        )
    )
    if result is None:
        raise UserNotFound()
    return result

async def _get_user_id_by_username(
        db: AsyncSession,
        username: str 
) -> UUID:
    result = await db.execute(
        select(User.id)
        .where(
            User.username == username
            )
    )
    user_id = result.scalar_one_or_none()
    if user_id is None:
        raise UserNotFound()
    return user_id

async def _get_user_id_by_phone(
        db: AsyncSession,
        phone: str 
) -> UUID:
    result = await db.execute(
        select(User.id)
        .where(
            User.phone == phone
            )
    )
    user_id = result.scalar_one_or_none()
    if user_id is None:
        raise UserNotFound()
    return user_id

async def _get_user_id_by_email(
        db: AsyncSession,
        email: str 
) -> UUID:
    result = await db.execute(
        select(User.id)
        .where(
            User.email == email
            )
    )
    user_id = result.scalar_one_or_none()
    if user_id is None:
        raise UserNotFound()
    return user_id