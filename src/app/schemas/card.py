from pydantic import BaseModel, Field
from datetime import date

from app.persistence.cards.card import Card


class CardResponse(BaseModel):
    id: int
    card_number: int
    expiration_date: date
    cardholder_name: str
    cvv: int

    @classmethod
    def create(cls, obj: Card) -> "CardResponse":
        return CardResponse(
            id=obj.id,
            card_number=obj.card_number,
            expiration_date=obj.expiration_date,
            cardholder_name=obj.cardholder_name,
            cvv=obj.cvv,
        )


class CardCreate(BaseModel):
    id: int
    card_number: int = Field(
        ...,
        regex=r'^\d{16}$',
        description="Exactly 16 digits, no spaces or dashes"
    )
    expiration_date: date
    cardholder_name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="2 to 30 characters"
    )
    cvv: int = Field(
        ...,
        regex=r'^\d{3}$',
        description="Exactly 3 digits, no spaces or dashes"
    )
    