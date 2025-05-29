from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.category import CategoryRead
from app.services.categories_service import get_all_categories
from app.persistence.db import get_session

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryRead])
async def read_categories(session: AsyncSession = Depends(get_session)):
    return await get_all_categories(session)
