from datetime import datetime

from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token:str
    token_type:str
    expiry:datetime

class TokenCollection(BaseModel):
    access:TokenResponse
    refresh:TokenResponse

