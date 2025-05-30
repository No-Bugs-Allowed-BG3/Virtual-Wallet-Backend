from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import date

from sqlalchemy import Transaction

class AdminTransactionResponse(BaseModel):
    id: UUID
    sender_username: str
    currency_code: str
    receiver_username: str
    category_name: str
    amount: Decimal
    status: str
    is_recurring: bool
    created_date: date

    class Config:
        orm_mode = True