from app.persistence.users.users import User
from app.persistence.user_devices.user_device import UserDevice
from app.schemas.user import UserLogin
from schemas.token import TokenCollection,TokenResponse
from services.errors import ServiceError
from services.utils.token_functions import create_tokens,create_device_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,insert
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

async def login_user_device(session:AsyncSession,usr:UserLogin,device_id:str)->TokenResponse|bool:
    if not usr.username or not usr.password:
        return False

    async def _login_device():
        statement = select(User).where(User.username==usr.username)
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()

        if not user_object:
            return False

        if not verify_password(usr.password,user_object.password):
            return False
        #check if device is already recorded , otherwise add it
        statement = select(UserDevice).where((UserDevice.user_id==user_object.id)
                                             & (UserDevice.device_id == device_id))
        result = await session.execute(statement)
        device_object = result.scalar_one_or_none()

        if not device_object:
            statement = insert(UserDevice).values(device_id=device_id,user_id=user_object.id)
            result = await session.execute(statement)
            await session.commit()
            if not result.rowcount:
                return ServiceError.ERROR_DURING_DEVICE_REGISTRATION

        return await create_device_token(user_object.id,user_object.is_admin)

    return await process_db_transaction(
        session=session,transaction_func=_login_device
    )
