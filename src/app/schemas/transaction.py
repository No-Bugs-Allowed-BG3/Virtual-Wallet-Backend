from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums.enums import AvailableCategory, AvailableCurrency, IntervalType


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

class TransactionCreate(BaseModel):
    receiver_username: str = Field(..., min_length=3, max_length=50, description="Username of the recipient")
    predefined_category: AvailableCategory | None = Field(
        ...,
        description="Name of the category in which this transaction falls under."
    )
    currency_code: AvailableCurrency = Field(
        ...,
        description="Code of the currency in which this transaction is executed."
    )
    card_number: str = Field(...,min_length=16, max_length=16)
    category_name: str | None = Field(None, min_length=2, max_length=50, description="Name of a new category (if not choosing from existing)")
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
    category_id: UUID | None = None
    amount: Decimal
    status: str
    is_recurring: bool
    created_date: date
    description: str | None = None
    sender_card_number: str | None = None
    receiver_card_number: str | None = None
    is_internal_transfer: bool = False

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

class CardToCardTransaction(BaseModel):
    sender_card_number: str = Field(..., min_length=16, max_length=16)
    receiver_card_number: str = Field(..., min_length=16, max_length=16)
    amount: Decimal = Field(..., gt=0)
    description: str | None = None

    class Config:
        allow_population_by_field_name = True

class CardToCardTransactionIn(BaseModel):
    sender_card_number: str
    receiver_card_number: str
    amount: Decimal
    description: str | None = None

class CardToCardTransactionOut(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    currency_id: UUID
    category_id: UUID | None = None
    amount: Decimal
    status: str
    is_recurring: bool
    created_date: date
    description: str | None = None
    sender_card_number: str | None = None
    receiver_card_number: str | None = None
    is_internal_transfer: bool = False

    class Config:
        orm_mode = True

