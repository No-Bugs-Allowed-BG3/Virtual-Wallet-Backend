from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel,EmailStr
import uuid

from app.persistence.users.users import User


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    is_blocked:bool
    is_activated:bool
    is_verified:bool

    @classmethod
    def create(cls, obj: User) -> "UserResponse":
        return UserResponse(
            id=obj.id,
            username=obj.username,
            is_blocked=obj.is_blocked,
            is_activated=obj.is_activated,
            is_verified=obj.is_verified
        )


class UserCreate(BaseModel):
    username: str
    password: str
    email:EmailStr

class UserLogin(BaseModel):
    username:str
    password:str

    @classmethod
    def from_oauth2_form_data(cls,form_data:OAuth2PasswordRequestForm)->"UserLogin":
        return cls(
            username=form_data.username,
            password=form_data.password
        )