from typing import Any, List
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.exceptions import UserNotFound, ContactAlreadyExists, ContactNotFound

from app.persistence.contacts.contact import Contact
from app.persistence.users.users import User
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
    contact_id = await _find_user_id(db, username, phone, email)
    if not contact_id:
        raise UserNotFound()
    contact = Contact(user_id=user_id,contact_id=contact_id)
    db.add(contact)
    try:
        await db.flush()
        await db.commit()
        await db.refresh(contact)
    except IntegrityError:
        await db.rollback()
        raise ContactAlreadyExists()
    await db.refresh(contact, ["contact"])
    return ContactResponse.create(contact)

async def read_contacts(
        db: AsyncSession,
        user_id: UUID
) -> List[ContactResponse]:
    stmt = (
        select(
            User.username,
            User.phone,
            User.email
        )
        .join(Contact, Contact.contact_id == User.id)
        .where(
            Contact.user_id == user_id,
            Contact.is_deleted.is_(False)
            )
    )

    result = await db.execute(stmt)

    contacts = [
        ContactResponse(
            username=row.username,
            phone=row.phone,
            email=row.email,
        )
        for row in result.fetchall()
    ]

    if not contacts:
        raise ContactNotFound()

    return contacts

async def _get_contact(
        db: AsyncSession,
        user_id: UUID,
        contact_id: UUID,
) -> Contact:
    result = await db.execute(
        select(Contact)
        .where(
            Contact.user_id == user_id,
            Contact.contact_id == contact_id,
            Contact.is_deleted.is_(False)
        )
    )
    if not result:
        raise ContactNotFound()
    return result

async def delete_contact(
        db: AsyncSession,
        user_id: UUID,
        contact_id: UUID
) -> None:
    result = await _get_contact(db, user_id, contact_id)
    if not result:
        raise UserNotFound()
    contact = result.scalar_one()
    contact.is_deleted = True
    await db.commit()