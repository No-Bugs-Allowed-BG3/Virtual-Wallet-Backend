from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.exceptions import USER_NOT_FOUND, CONTACT_ALREADY_EXISTS

from app.persistence.contacts.contact import Contact
from app.schemas.contact import ContactResponse
from app.services.users_service import _get_user_id_by_username, _get_user_id_by_email, _get_user_id_by_phone

async def _find_user_id(
    db: AsyncSession,
    username: str | None,
    phone: str | None,
    email: str | None
) -> UUID | None:
    if username:
        return await _get_user_id_by_username(db, username)
    if phone:
        return await _get_user_id_by_phone(db, phone)
    if email:
        return await _get_user_id_by_email(db, email)
    return None

async def create_contact(
    db: AsyncSession,
    user_id: UUID,
    username: str | None = None,
    phone: str | None = None,
    email: str | None = None
) -> ContactResponse:
    contact_id = _find_user_id(db, username, phone, email)
    if not contact_id:
        raise USER_NOT_FOUND
    contact = Contact(user_id=user_id,contact_id=contact_id)
    db.add(contact)
    try:
        await db.flush()
        await db.commit()
        await db.refresh(contact)
    except IntegrityError:
        await db.rollback()
        raise CONTACT_ALREADY_EXISTS
    return ContactResponse.create(contact)

