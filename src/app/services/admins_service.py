from typing import List
from app.api.exceptions import UserNotFound
from app.persistence.users.users import User
from app.schemas.user import AdminUserResponse
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

async def read_users(
        db: AsyncSession
) -> List[AdminUserResponse]:
    stmt = (
        select(
            User.id,
            User.username,
            User.email,
            User.phone,
            User.is_blocked,
            User.is_activated,
            User.is_verified,
            User.is_admin,
            User.avatar
        )
    )

    result = await db.execute(stmt)

    users = [
        AdminUserResponse(
            id=row.id,
            username=row.username,
            email=row.email,
            phone=row.phone,
            is_blocked=row.is_blocked,
            is_activated=row.is_activated,
            is_verified=row.is_verified,
            is_admin=row.is_admin,
            avatar=row.avatar
        )
        for row in result.fetchall()
    ]

    if not users:
        raise UserNotFound()

    return users