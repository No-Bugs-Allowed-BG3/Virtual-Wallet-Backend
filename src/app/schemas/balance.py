from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.enums.enums import AvailableCurrency
from app.persistence.balances.balance import Balance


class BalanceResponse(BaseModel):
    id: UUID
    amount: Decimal
    currency_code: AvailableCurrency

    @classmethod
    def create(cls, obj: Balance) -> "BalanceResponse":
        return BalanceResponse(
            id=obj.id,
            amount=obj.amount,
            currency_code=obj.currency.code
        )