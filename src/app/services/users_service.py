from app.persistence.users.users import User
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.utils.security import get_password_hash
from app.services.utils.processors import process_db_transaction
from app.services.utils.mail.sendmail import send_activation_mail
from app.core.auth.token_functions import decode_access_token,decode_refresh_token

async def create_user(session:AsyncSession ,user: UserCreate) -> UserResponse:
    async def _create():
        user.password = get_password_hash(user.password)
        db_obj = User(**user.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        await send_activation_mail(to_email=user.email,to_username=user.username)
        return UserResponse.create(db_obj)

    return await process_db_transaction(
        session=session,
        transaction_func=_create,
    )
