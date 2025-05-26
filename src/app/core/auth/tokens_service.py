from app.persistence.users.users import User
from app.schemas.user import UserLogin
from app.core.auth.token_model import TokenCollection
from app.core.auth.token_functions import create_tokens
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.utils.security import verify_password
from app.services.utils.processors import process_db_transaction

async def login_user(session:AsyncSession,usr:UserLogin)->TokenCollection|bool:
    if not usr.username or not usr.password:
        return False
    async def _login():
        statement = select(User).where(User.username==usr.username)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()

        if not user_object:
            return False

        if not verify_password(usr.password,user_object.password):
            return False

        return await create_tokens(user_object.id,user_object.is_admin)

    return await process_db_transaction(
        session=session,transaction_func=_login
    )
