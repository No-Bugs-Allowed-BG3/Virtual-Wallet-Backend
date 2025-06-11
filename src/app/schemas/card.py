from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import date
from app.core.enums.enums import AvailableCurrency

from app.persistence.cards.card import Card


class CardResponse(BaseModel):
    card_number: str
    expiration_date: date
    cardholder_name: str

    @classmethod
    def create(cls, obj: Card) -> "CardResponse":
        return CardResponse(
            card_number=obj.card_number,
            expiration_date=obj.expiration_date,
            cardholder_name=obj.cardholder_name,
        )


class CardCreate(BaseModel):
    card_number: str = Field(
        ...,
        pattern=r'^\d{16}$',
        description="Exactly 16 digits, no spaces or dashes"
    )
    expiration_date: date
    cardholder_name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="2 to 30 characters"
    )
    cvv: str = Field(
        ...,
        pattern=r'^\d{3}$',
        description="Exactly 3 digits, no spaces or dashes"
    )
    currency_code: AvailableCurrency = Field(
        ...,
        description="Code of the currency in which this card operates."
    )
    amount: Decimal = Field(0, ge=0, description="Initial balance amount")