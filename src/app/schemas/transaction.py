from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from app.core.enums.enums import IntervalType
from datetime import date

class TransactionCreate(BaseModel):
    receiver_username: str = Field(..., min_length=3, max_length=50, description="Username of the recipient")
    category_id: UUID
    currency_id: UUID
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: str = Field(..., min_length=1, max_length=200, description="Reason or note for the transaction")
    is_recurring: bool = False
    interval_days: int | None = Field(None, gt=0, description="Interval in days for recurring transactions")
    next_run_date: date | None = Field(None, description="Date for next recurring transaction execution")

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

class RecurringTransactionCreate(BaseModel):
    receiver_username: str = Field(..., min_length=3, max_length=50, description="Username of the recipient")
    category_id: UUID
    currency_id: UUID
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: str = Field(..., min_length=1, max_length=200, description="Reason or note for the transaction")
    start_date: date = Field(..., description="Date when recurring transactions start")
    frequency: IntervalType = Field(..., description="How often the transaction repeats")
    end_date: date | None = Field(None, description="Optional end date for the recurring transactions")
    occurrences: int | None = Field(None, gt=0, description="Optional number of occurrences, alternative to end_date")
    is_active: bool = True