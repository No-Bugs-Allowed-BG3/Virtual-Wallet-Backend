from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship
import uuid
from app.persistence.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    recurring_transactions = relationship(
        "RecurringTransaction", back_populates="currency"
    )
    balances = relationship("Balance",back_populates="currency",cascade="all, delete-orphan")