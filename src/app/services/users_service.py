from app.api.exceptions import USER_NOT_FOUND
from app.persistence.users.users import User
from app.schemas.user import UserCreate, UserResponse,UserSettings,UserSettingsResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from sqlalchemy import update,select
from app.services.utils.security import get_password_hash,verify_password
from app.services.utils.processors import process_db_transaction
from app.services.utils.mail.sendmail import send_activation_mail
from app.services.errors import ServiceError
import requests
from os import getenv
import cloudinary
import cloudinary.uploader
from app.schemas.service_result import ServiceResult

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
        raise USER_NOT_FOUND
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
        raise USER_NOT_FOUND
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
        raise USER_NOT_FOUND
    return user_id