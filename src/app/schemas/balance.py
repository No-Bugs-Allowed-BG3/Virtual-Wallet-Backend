from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.persistence.balances.balance import Balance

class BalanceCreate(BaseModel):
    amount: Decimal

class BalanceResponse(BaseModel):
    card_number: str = Field(..., min_length=16, max_length=16)
    amount: Decimal
    currency_code: str

    @classmethod
    def create(cls, obj: Balance) -> "BalanceResponse":
        return BalanceResponse(
            id=obj.id,
            amount=obj.amount,
            currency_code=obj.currency.code
        )

