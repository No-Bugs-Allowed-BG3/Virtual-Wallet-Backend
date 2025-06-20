import asyncio
import uuid

from sqlalchemy import select
from app.core.config import settings
from app.persistence.db import initialize_database, get_session
from app.persistence.db import Base 
from app.persistence.db import engine  
from app.persistence.currencies.currency import Currency 
from app.persistence.categories.categories import Category 
from app.core.enums.enums import AvailableCurrency

PREDEFINED_CATEGORIES = [
    "groceries",
    "utilities",
    "transport",
    "entertainment",
    "User Transfer"
]
async def create_predefined_categories(session):
    result = await session.execute(select(Category.name))
    existing_names = {row[0] for row in result.all()}

    to_add = []
    for name in PREDEFINED_CATEGORIES:
        if name not in existing_names:
            to_add.append(Category(id=uuid.uuid4(), name=name, is_default = True))

    if to_add:
        session.add_all(to_add)
        await session.commit()
        print(f"Inserted categories: {[c.name for c in to_add]}")
    else:
        print("All categories already present; no inserts performed.")

async def load_initial_currencies():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async for session in get_session():
        result = await session.execute(select(Currency.code))
        existing_codes = {row[0] for row in result.all()}

        to_add = []
        for cur in AvailableCurrency:
            code = cur.value.upper()
            name = cur.name.title() 
            if code not in existing_codes:
                to_add.append(
                    Currency(
                        id=uuid.uuid4(),
                        code=code,
                        name=name
                    )
                )

        if to_add:
            session.add_all(to_add)
            await session.commit()
            print(f"Inserted currencies: {[c.code for c in to_add]}")
        else:
            print("All currencies already present; no inserts performed.")


async def main():
    await load_initial_currencies()

    async for session in get_session():
        await create_predefined_categories(session)

if __name__ == "__main__":
    asyncio.run(main())
