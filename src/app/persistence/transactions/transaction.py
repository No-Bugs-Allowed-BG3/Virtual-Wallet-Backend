from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, Boolean, Date, String
from app.persistence.users.users import User
from app.persistence.currencies.currency import Currency
from app.persistence.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.persistence.categories.categories import Category

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    currency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("currencies.id"))
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))

    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    created_date: Mapped[Date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String, nullable=True)

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], backref="sent_transactions")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id], backref="received_transactions")
    currency: Mapped["Currency"] = relationship("Currency", backref="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")

