from jose import jwt, JWTError
from datetime import datetime,timedelta,timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from schemas.token import TokenResponse,TokenCollection
from sqlalchemy import select
from app.persistence.users.users import User
from app.persistence.db import get_session
from app.services.utils.processors import process_db_transaction
from app.schemas.user import UserResponse
from fastapi import Cookie,Depends
from typing import Annotated
from api.exceptions import USER_UNAUTHORIZED

import uuid

async def create_access_token(user_id:uuid.UUID,is_admin:bool)->TokenResponse:
    """
    Args:
        user_id: ID of the user for whom the Token is created
        is_admin: Boolean value True or False indicating whether the user is
                  a regular user or an admin

    The expiry,algorithm and encryption key of the Token are
    configured in the src.app.core.config.py file.

    Returns: An object indicating the type of Token, in this case "access"
             and the encoded payload of the token
    """
    expiry:datetime = (datetime.now(timezone.utc) +
                       timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    data_to_encode = {
        "sub":str(user_id),
        "exp":expiry,
        "admin":is_admin
    }
    encoded_access_token_data = jwt.encode( claims=data_to_encode,
                                            key=settings.ACCESS_TOKEN_SECRET_KEY,
                                            algorithm=settings.TOKEN_ALGORITHM )
    return TokenResponse(access_token=encoded_access_token_data,
                         token_type="access",
                         expiry=expiry)

async def create_refresh_token(user_id:uuid.UUID,is_admin:bool)->TokenResponse:
    """
    Args:
        user_id: ID of the user for whom the Token is created
        is_admin: Boolean value True or False indicating whether the user is
                  a regular user or an admin

    The expiry,algorithm and encryption key of the Token are
    configured in the src.app.core.config.py file.

    Returns: An object indicating the type of Token, in this case "refresh"
             and the encoded payload of the token
    """
    expiry:datetime = (datetime.now(timezone.utc) +
                       timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    data_to_encode = {
        "sub":str(user_id),
        "exp":expiry,
        "admin":is_admin
    }
    encoded_access_token_data = jwt.encode( claims=data_to_encode,
                                            key=settings.ACCESS_TOKEN_SECRET_KEY,
                                            algorithm=settings.TOKEN_ALGORITHM )
    return TokenResponse(access_token=encoded_access_token_data,
                        token_type="refresh",
                        expiry=expiry)

async def decode_access_token(encoded_token_data:str)->bool|dict:
    """
    Args:
        encoded_token_data: The encoded token data received from the cookie which has been set
        during login.
    Returns:
        Boolean ( False ) if there is an error while encoding, the Token has expired or data is
        corrupted in some way.
        Dictionary, containing the information about the user :
            sub : ID of the user
            exp : Expiry of the Token
            admin : True or False , indicating whether the user is an admin or not
    """
    try:
        token_payload = jwt.decode(token=encoded_token_data,
                                   key=settings.ACCESS_TOKEN_SECRET_KEY,
                                   algorithms=[settings.TOKEN_ALGORITHM])
    except JWTError:
        return False
    if not token_payload:
        return False
    return token_payload

async def decode_refresh_token(encoded_token_data:str)->bool|TokenResponse:
    """
    Args:
        encoded_token_data: The encoded token data received from the cookie which has been set
        during login.
    Returns:
        Boolean ( False ) if there is an error while encoding, the Token has expired or data is
        corrupted in some way.
        Token which is a renewed access Token.
    """
    try:
        token_payload = jwt.decode(token=encoded_token_data,
                                   key=settings.ACCESS_TOKEN_SECRET_KEY,
                                   algorithms=[settings.TOKEN_ALGORITHM])
    except JWTError:
        return False
    if not token_payload:
        return False
    decoded_user_id:uuid.UUID|None = token_payload.get("sub",None)
    decoded_is_admin:bool|None = token_payload.get("admin",None)
    if decoded_user_id is None or decoded_is_admin is None:
        return False
    return await create_access_token(decoded_user_id,decoded_is_admin)

async def create_tokens(user_id:uuid.UUID,is_admin:bool)->TokenCollection:
    """
    Args:
        user_id: ID of the user for whom the Token is created
        is_admin: Boolean value True or False indicating whether the user is
                  a regular user or an admin

    Returns:
        A collection containing both access and refresh tokens

    """
    return TokenCollection(
        access=await create_access_token(user_id=user_id,is_admin=is_admin),
        refresh=await create_refresh_token(user_id=user_id,is_admin=is_admin)
    )

async def get_current_user(session:Annotated[AsyncSession,Depends(get_session)],access_token:Annotated[str|None,Cookie()]=None)->UserResponse|bool|dict:
    """

    Args:
        session:
        access_token:

    Returns:


    """
    if not access_token:
        raise USER_UNAUTHORIZED
    token_data = await decode_access_token(access_token)
    if not token_data:
        raise USER_UNAUTHORIZED
    async def _get_current_user_from_db():
        statement = select(User).where(User.id==token_data.get("sub"))
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            raise USER_UNAUTHORIZED
        return UserResponse(
            id = user_object.id,
            username=user_object.username,
            is_blocked=user_object.is_blocked,
            is_verified=user_object.is_verified,
            is_activated=user_object.is_activated,
            is_admin=user_object.is_admin,
            avatar=user_object.avatar
        )

    return await process_db_transaction(
        session=session,
        transaction_func=_get_current_user_from_db
    )

async def user_can_interact(session:Annotated[AsyncSession,Depends(get_session)],access_token:Annotated[str|None,Cookie()]=None)->bool:
    """
    Args:
        session:
        access_token: Gets the __HTTP-Only__ "access_token" cookie set
        during login

    Returns:
        A boolean representation indicating whether the user can "interact" with
        the functionality
    """
    if not access_token:
        raise USER_UNAUTHORIZED
    session_generator = get_session()
    session = await anext(session_generator)
    token_data = await decode_access_token(access_token)
    if not token_data:
        raise USER_UNAUTHORIZED

    async def _get_current_user_from_db():
        statement = select(User).where(User.id == token_data.get("sub"))
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            raise USER_UNAUTHORIZED
        if user_object.is_activated and user_object.is_verified:
            return True
        return False

    return await process_db_transaction(
        session=session,
        transaction_func=_get_current_user_from_db
    )

async def user_can_make_transactions(session:Annotated[AsyncSession,Depends(get_session)],access_token:Annotated[str|None,Cookie()]=None)->bool:
    """
    Args:
        session:
        access_token: Gets the __HTTP-Only__ "access_token" cookie set
        during login

    Returns:
        A boolean representation indicating whether the user can perform money
        transactions
    """
    if not access_token:
        raise USER_UNAUTHORIZED
    session_generator = get_session()
    session = await anext(session_generator)
    token_data = await decode_access_token(access_token)
    if not token_data:
        raise USER_UNAUTHORIZED

    async def _get_current_user_from_db():
        statement = select(User).where(User.id == token_data.get("sub"))
        result = await session.execute(statement)
        user_object = result.scalar_one_or_none()
        if not user_object:
            raise USER_UNAUTHORIZED
        if (user_object.is_activated and
                user_object.is_verified and
                not user_object.is_blocked):
            return True
        return False

    return await process_db_transaction(
        session=session,
        transaction_func=_get_current_user_from_db
    )