from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession
from app.core.config import settings
# from app.persistence.balances.balance import Balance
# from app.persistence.cards.card import Card
# from app.persistence.categories.categories import Category
# from app.persistence.contacts.contact import Contact
# from app.persistence.currencies.currency import Currency
# from app.persistence.recurring_transactions.recurring_transaction import RecurringTransaction
# from app.persistence.transactions.transaction import Transaction
# from app.persistence.users.users import User

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass


async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session