from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import UserUnauthorized
from app.schemas.transaction import AdminTransactionResponse
from app.services.utils.token_functions import admin_status
from app.persistence.db import get_session
from app.schemas.user import AdminUserResponse
from app.services.admins_service import block_user, read_users, read_transactions, unblock_user

router = APIRouter(prefix="/admin", tags=["Admin panel"])


@router.get(
    "/registered_users",
    response_model=List[AdminUserResponse]
)
async def get_users(
    admin_status: bool = Depends(admin_status),
    db: AsyncSession = Depends(get_session)
) -> List[AdminUserResponse]:
    if not admin_status:
        raise UserUnauthorized()
    return await read_users(db=db)

@router.get(
    "/created_transactions",
    response_model=List[AdminTransactionResponse]
)
async def get_transactions(
    admin_status: bool = Depends(admin_status),
    db: AsyncSession = Depends(get_session),
    start_date: date | None = None,
    end_date: date | None = None,
    sender_username: str | None = None,
    receiver_username: str | None = None,
    direction: str | None = None,
    user_id: UUID | None = None,
    limit: int = 20,
    offset: int = 0
) -> List[AdminTransactionResponse]:
    if not admin_status:
        raise UserUnauthorized()
    return await read_transactions(db=db,start_date=start_date,
        end_date=end_date,
        sender_username=sender_username,
        receiver_username=receiver_username,
        direction=direction,
        user_id=user_id,
        limit=limit,
        offset=offset)

@router.post(
    "/registered_users/{user_id}"
)
async def block_user_transactions(
    user_id: UUID,
    admin_status: bool = Depends(admin_status),
    db: AsyncSession = Depends(get_session)
):
    if not admin_status:
        raise UserUnauthorized()
    return await block_user(db, user_id)

@router.put(
    "/registered_users/{user_id}"
)
async def unblock_user_transactions(
    user_id: UUID,
    admin_status: bool = Depends(admin_status),
    db: AsyncSession = Depends(get_session)
):
    if not admin_status:
        raise UserUnauthorized()
    return await unblock_user(db, user_id)