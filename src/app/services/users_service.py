from app.persistence.users.users import User
from app.schemas.user import UserCreate, UserResponse,UserSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update,select
from app.services.utils.security import get_password_hash
from app.services.utils.processors import process_db_transaction
from app.services.utils.mail.sendmail import send_activation_mail
from app.services.errors import ServiceError
import requests
from os import getenv
import cloudinary
import cloudinary.uploader
from app.schemas.service_result import ServiceResult

from schemas.user import UserSettingsResponse


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

async def activate_user(current_user:UserResponse,session:AsyncSession) -> ServiceResult|ServiceError:
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
    print(service_result)
    return ServiceResult(
        result=service_result
    )


async def update_user_settings(current_user:UserResponse,
                               session:AsyncSession,
                               settings:UserSettings) -> ServiceResult|ServiceError:
    async def _update_settings():
        if settings.password == getenv("USER_SAMPLE_PASSWORD"):
            statement = update(User).where(User.id == current_user.id).values(
                email=settings.email,
                phone=settings.phone
                )
        else:
            settings.password = get_password_hash(settings.password)
            statement = update(User).where(User.id == current_user.id).values(
                email=settings.email,
                password=settings.password,
                phone=settings.phone
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
    return_result = ServiceResult(
        result=service_result
    )
    print(isinstance(return_result,ServiceResult))
    return return_result

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