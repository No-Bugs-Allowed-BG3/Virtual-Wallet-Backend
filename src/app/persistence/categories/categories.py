from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, Boolean, UniqueConstraint
from typing import TYPE_CHECKING
from app.persistence.db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
if TYPE_CHECKING:
    from app.persistence.users.users import User
    from app.persistence.transactions.transaction import Transaction

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="category")
    user: Mapped["User"] = relationship("User", back_populates="categories")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_category_name_per_user"),)

