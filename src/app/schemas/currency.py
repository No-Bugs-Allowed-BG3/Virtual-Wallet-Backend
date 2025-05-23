from pydantic import BaseModel, field_validator

class Currency(BaseModel):
    id: int
    code: str
    name: str

class CurrencyCreate(BaseModel):
    code: str
    name: str

    @field_validator("code")
    def code_must_be_3_letters(cls, v):
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Code must be exactly 3 letters")
        return v.upper()

class CurrencyResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        orm_mode = True
