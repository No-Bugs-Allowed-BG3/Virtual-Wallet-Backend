from enum import Enum
from fastapi import HTTPException

class IntervalType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    @staticmethod
    def get_interval_type_from_days(days: int | None):
        if days is None:
            raise HTTPException(status_code=400, detail="Interval days must be specified for recurring transactions")

        if days == 1:
            return IntervalType.DAILY
        elif days == 7:
            return IntervalType.WEEKLY
        elif 28 <= days <= 31:
            return IntervalType.MONTHLY
        elif 365 <= days <= 366:
            return IntervalType.YEARLY
        else:
            raise HTTPException(status_code=400, detail="Unsupported interval_days value")


class AvailableCurrency(str, Enum):
    USD = "usd"
    GBP = "gbp"
    EUR = "eur"
    INR = "inr"
    BGN = "bgn"