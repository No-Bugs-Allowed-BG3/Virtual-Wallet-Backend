from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.users.users import User
from app.services.utils.security import get_password_hash


async def create_admin_user(session: AsyncSession):
    result = await session.execute(select(User).where(User.is_admin == True))
    admin_user = result.scalars().first()

    if admin_user:
        return
    
    admin_data = {"username": "admin",
                  "email": "admin@admin.com",
                  "password": get_password_hash("StrongestPass123@"),
                  "is_admin": True,
                  "phone": "012345678"}
    
    admin = User(**admin_data)
    session.add(admin)
    await session.commit()