from uuid import UUID
from typing import Any, List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.contact import ContactResponse, ContactCreate
from app.schemas.user import UserResponse, User as CurrentUser
from app.services.contacts_service import create_contact, read_contacts, delete_contact, search_contact

router = APIRouter(prefix="/users/me/contacts", tags=["contacts"])

@router.post(
    "/", 
    response_model=ContactResponse
)
async def add_contact(
    contact: ContactCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await create_contact(
        db=db,
        user_id=current_user.id,
        username=contact.username,
        phone=contact.phone,
        email=contact.email,
        )

@router.get(
    "/",
    response_model=List[ContactResponse]
)
async def get_contacts(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await read_contacts(
        db=db,
        user_id=current_user.id,
    )

@router.delete(
    "/{contact_id}/"
)
async def remove_contact(
    contact_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await delete_contact(
        user_id=current_user.id,
        contact_id=contact_id,
        db=db
    )

@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    search_by: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await search_contact(db=db, user_id=current_user.id, query=search_by)