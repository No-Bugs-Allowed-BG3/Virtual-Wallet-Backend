import uuid
from typing import List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.categories.categories import Category
from app.schemas.category import CategoryCreate
from fastapi import HTTPException

async def get_all_categories(session: AsyncSession, user_id: uuid.UUID) -> List[Category]:
    result = await session.execute(
        select(Category).where(
            Category.is_deleted.is_(False),
            or_(
                Category.user_id.is_(None),
                Category.user_id == user_id  
            )
        )
    )
    return result.scalars().all()

async def get_category_by_id(session: AsyncSession, category_id: uuid.UUID) -> Category | None:
    result = await session.execute(
        select(Category).where(Category.id == category_id, Category.is_deleted.is_(False))
    )
    return result.scalar_one_or_none()

async def get_category_by_name(session: AsyncSession, category_name:str) -> Category | None:
    result = await session.execute(select(Category).where(Category.name == category_name, Category.is_deleted.is_(False)))
    return result.scalar_one_or_none()

async def _get_category_id_by_name(session: AsyncSession, category_name:str) -> Category | None:
    result = await session.execute(select(Category).where(Category.name == category_name, Category.is_deleted.is_(False)))
    return result.id

async def create_category(session: AsyncSession, user_id: uuid.UUID,category_data: CategoryCreate) -> Category:
    new_category = Category(id=uuid.uuid4(), name=category_data.name, user_id = category_data.user_id)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category

async def soft_delete_category(session: AsyncSession, category_id: uuid.UUID):
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    category.is_deleted = True
    await session.commit()
    await session.refresh(category)
    return category

async def category_exists(session: AsyncSession, category_id: uuid.UUID):
    result = await session.execute(select(Category).where(Category.id == category_id, Category.is_deleted.is_(False)))
    existing_category = result.scalar_one_or_none()
    if existing_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return existing_category