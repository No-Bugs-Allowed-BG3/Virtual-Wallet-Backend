import uuid
from sqlalchemy.dialects.postgresql import UUID

from typing import TYPE_CHECKING, List
from datetime import date
from sqlalchemy import ForeignKey, Integer, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.db import Base

if TYPE_CHECKING:
    from app.persistence.balances.balance import Balance


class Card(Base):
    """
    Represents a Card entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier of the card.
        balance_id (uuid.UUID): FK to the Balance owning this balance.
        card_number (int): 16-Digit number of the card.
        expiration_date (datetime): Datetime object of the expiration date of the card.
        cardholder_name (str): Name of the cardholder.
        cvv (int): 3-Digit CVV of the card.
        design_image (str): Link to design image handled by external service Cloudinary.

    Relationships:
        balance (Balance): Balance associated with this card.
    """

    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    balance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("balances.id"),
        nullable=False,
    )

    card_number: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        unique=True,
    )

    expiration_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    cardholder_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    cvv: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    design_image: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # --- Relationships ---
    balance: Mapped["Balance"] = relationship(
        "Balance",
        back_populates="cards",
    )