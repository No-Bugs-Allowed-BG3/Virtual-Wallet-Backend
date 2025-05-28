from enum import Enum

class IntervalType(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class AvailableCurrency(str, Enum):
    USD = "usd"
    GBP = "gbp"
    EUR = "eur"
    INR = "inr"
    BGN = "bgn"