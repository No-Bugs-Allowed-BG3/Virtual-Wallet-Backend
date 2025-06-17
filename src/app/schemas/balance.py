from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.persistence.balances.balance import Balance

class BalanceCreate(BaseModel):
    amount: Decimal

class BalanceResponse(BaseModel):
    id: UUID
    amount: Decimal
    currency_code: str

    @classmethod
    def create(cls, obj: Balance) -> "BalanceResponse":
        return BalanceResponse(
            id=obj.id,
            amount=obj.amount,
            currency_code=obj.currency.code
        )

class BalanceRequest(BaseModel):
    amount: str
    currency_code: str
    cvv_code:str
    expiry:str
    card_number:str