from sqlalchemy import BigInteger, Column, ForeignKey, Numeric, Boolean, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid 
from app.persistence.db import Base
from app.core.enums.enums import IntervalType
from sqlalchemy.dialects.postgresql import UUID

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    currency_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("currency.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric, nullable=False)
    interval_type: Mapped[IntervalType] = mapped_column(Enum(IntervalType), nullable=False)
    next_execution_date: Mapped = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_recurring_transactions")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_recurring_transactions")
    currency = relationship("Currency", back_populates="recurring_transactions")
