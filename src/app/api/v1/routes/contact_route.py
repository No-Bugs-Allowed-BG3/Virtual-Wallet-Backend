from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.utils.token_functions import get_current_user
from app.persistence.db import get_session
from app.schemas.contact import ContactResponse, ContactCreate
from app.schemas.user import UserResponse
from app.services.contacts_service import create_contact

router = APIRouter(prefix="/users/me/contacts", tags=["contacts"])

@router.post(
    "/", 
    response_model=ContactResponse, 
    status_code=status.HTTP_201_CREATED
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