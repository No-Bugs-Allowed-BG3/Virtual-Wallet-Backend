import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from app.persistence.db import Base

if TYPE_CHECKING:
    from app.persistence.cards.card import Card
    from app.persistence.users.users import User
    from app.persistence.currencies.currency import Currency


class Balance(Base):
    """
    Represents a Balance entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier of the balance.
        user_id (uuid.UUID): FK to the User owning this balance.
        currency_id (uuid.UUID): FK to the Currency of this balance.
        amount (int): Amount of money in this balance.

    Relationships:
        user (User): owner of this balance.
        currency (Currency): the currency of this balance.
        cards (List[Card]): all cards linked to this balance.
    """

    __tablename__ = "balances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="balances",
    )
    currency: Mapped["Currency"] = relationship(
        "Currency",
        back_populates="balances",
    )
    cards: Mapped[List["Card"]] = relationship(
        "Card",
        back_populates="balance",
        cascade="all, delete-orphan",
    )