import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.users.users import User

from app.persistence.db import Base

class Contact(Base):
    """
    Represents a Contact entity in the database.

    Attributes:
        id (uuid): Unique identifier of the contact.
        user_id (UUID): Foreign key to the User sending funds.
        contact_id (UUID): Foreign key to the User receiving funds.
        is_deleted (bool): ...
    
    Relationships:
        user (User): The User who listed the contact.
        contact (User): The User who is listed as contact.
    """

    __tablename__ = "contacts"

    __table_args__ = (
        UniqueConstraint("user_id", "contact_id", name="uix_user_contact"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="contacts"
    )

    contact: Mapped["User"] = relationship(
        "User", foreign_keys=[contact_id]
    )