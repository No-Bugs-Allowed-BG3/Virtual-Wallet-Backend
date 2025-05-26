from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.persistence.db import Base

if TYPE_CHECKING:
    from app.persistence.balances.balance import Balance
    from app.persistence.transactions.transaction import Transaction
    from app.persistence.recurring_transactions.recurring_transaction import RecurringTransaction
    from app.persistence.contacts.contact import Contact

class User(Base):
    """
    Represents a User entity in the database.

    Attributes:
        id (UUID): Unique identifier of the user.
        username (str): Username of the user.
        email (str): E-mail of the user.
        password (str): Password hash.
        is_blocked (bool): Blocked status of the user.
        is_admin (bool): Admin role flag.
        is_verified (bool): Email verification status.
        avatar (str): URL to the user's avatar image.

    Relationships:
        balances (List[Balance]): All balances owned by the user.
        sent_transactions (List[Transaction]): Transactions this user has sent.
        received_transactions (List[Transaction]): Transactions this user has received.
        sent_recurring_transactions (List[RecurringTransaction]): Recurring templates created by the user to send funds.
        received_recurring_transactions (List[RecurringTransaction]): Recurring templates created to receive funds.
        contacts (List[Contact]): Contacts added by the user.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    phone:Mapped[str] = mapped_column(String,nullable=False)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_activated : Mapped[bool] = mapped_column(Boolean, default=False,nullable=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)

    balances: Mapped[List["Balance"]] = relationship(
        "Balance", back_populates="user", cascade="all, delete-orphan"
    )
    # Transactions are available via the backrefs defined in Transaction
    sent_recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship(
        "RecurringTransaction", foreign_keys="[RecurringTransaction.sender_id]",
        back_populates="sender", cascade="all, delete-orphan"
    )
    received_recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship(
        "RecurringTransaction", foreign_keys="[RecurringTransaction.receiver_id]",
        back_populates="receiver", cascade="all, delete-orphan"
    )
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Contact.user_id]"
    )
