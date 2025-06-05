from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.category import CategoryRead
from app.services.categories_service import get_all_categories
from app.persistence.db import get_session
from app.services.utils.token_functions import get_current_user


router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryRead])
async def read_categories(session: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    return await get_all_categories(session, current_user.id)
