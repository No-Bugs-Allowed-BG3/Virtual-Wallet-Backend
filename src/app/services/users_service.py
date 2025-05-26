from app.persistence.users.users import User
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from app.services.utils.security import get_password_hash
from app.services.utils.processors import process_db_transaction
from app.services.utils.mail.sendmail import send_activation_mail
from app.services.errors import ServiceError
import requests
from os import getenv

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

async def activate_user(current_user:UserResponse,session:AsyncSession) -> bool|ServiceError:
    async def _activate():
        statement = update(User).where(User.id == current_user.id).values(is_activated=True)
        result = await session.execute(statement)
        await session.commit()
        if result.rowcount:
            return True
        return ServiceError.ERROR_USER_NOT_FOUND

    return await process_db_transaction(
        session=session,
        transaction_func=_activate,
    )

async def verify_user(current_user:UserResponse,
                 id_document:bytes,
                 selfie:bytes,
                 session:AsyncSession)->bool|ServiceError:
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
    return verification_result

