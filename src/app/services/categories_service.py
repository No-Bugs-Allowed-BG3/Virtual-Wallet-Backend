import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.categories.categories import Category
from app.schemas.category import CategoryCreate

async def get_all_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(select(Category))
    return result.scalars().all()

async def get_category_by_id(session: AsyncSession, category_id: uuid.UUID) -> Category | None:
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()

async def create_category(session: AsyncSession, category_data: CategoryCreate) -> Category:
    new_category = Category(id=uuid.uuid4(), name=category_data.name)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category