from pydantic import BaseModel, field_validator
from enum import Enum
from api.exceptions import PINIncorrectFormat
from uuid import UUID
from typing import List

class TargetEnum(Enum):
    transaction = "transaction"
    payment = "payment"

class ConfirmationRequest(BaseModel):
    user_pin:str
    @field_validator('user_pin')
    @classmethod
    def _validate_user_pin(cls,value:str)->str:
        for c in value:
            if not c.isnumeric():
                raise PINIncorrectFormat()
        return value

    confirmation_target:TargetEnum
    confirmation_target_id:UUID

class ConfirmationItem(BaseModel):
    confirmation_target:TargetEnum
    confirmation_target_id:UUID
    receiver:str|None=None

class ConfirmationItemCollection(BaseModel):
    confirmation_items:List[ConfirmationItem]

class ConfirmationResponse(ConfirmationItem):
    confirmation_result:bool
