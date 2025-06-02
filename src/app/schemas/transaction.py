from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import date

class TransactionCreate(BaseModel):
    receiver_username: str = Field(..., min_length=3, max_length=50, description="Username of the recipient")
    category_id: UUID
    currency_id: UUID
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: str = Field(..., min_length=1, max_length=200, description="Reason or note for the transaction")
    is_recurring: bool = False

class TransactionResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    currency_id: UUID
    category_id: UUID
    amount: Decimal
    status: str
    is_recurring: bool
    created_date: date
    description: str | None = None

    class Config:
        orm_mode = True