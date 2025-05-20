from app.crud.users.user import User
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession


from app.services.utils.security import get_password_hash
from app.services.utils.processors import process_db_transaction


async def create_user(session: AsyncSession, user: UserCreate) -> UserResponse:
    async def _create():
        db_obj = User.model_validate(
            user, update={"password": get_password_hash(user.password)}
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return UserResponse.create(db_obj)

    return await process_db_transaction(
        session=session,
        func=_create,
    )
