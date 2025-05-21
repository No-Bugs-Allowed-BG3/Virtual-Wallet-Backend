from pydantic import BaseModel

class Token(BaseModel):
    token_encoded_data:str
    token_type:str

