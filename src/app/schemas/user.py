from app.api.exceptions import PASSWORD_INCORRECT_FORMAT,USERNAME_INCORRECT_FORMAT
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel,EmailStr,field_validator
from pydantic.types import StringConstraints
import uuid
from typing import Annotated
from app.persistence.users.users import User

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    is_blocked:bool
    is_activated:bool
    is_verified:bool
    is_admin:bool
    avatar:str|None=None

    @classmethod
    def create(cls, obj: User) -> "UserResponse":
        return UserResponse(
            id=obj.id,
            username=obj.username,
            is_blocked=obj.is_blocked,
            is_activated=obj.is_activated,
            is_verified=obj.is_verified,
            is_admin=obj.is_admin
        )

class UserSettings(BaseModel):
    email:EmailStr
    phone:Annotated[str,StringConstraints(max_length=13,min_length=10,pattern=r"^\+?(\d{10}|\d{12})$")]
    @field_validator('phone')
    @classmethod
    def _strip_plus(cls,value:str)->str:
        return value.replace("+","")

    @classmethod
    def create(cls, obj: User) -> "UserSettings":
        return UserSettings(
            email=obj.email,
            phone=obj.phone,
        )

class UserSettingsResponse(BaseModel):
    email:EmailStr
    phone:str
    avatar:str|None

    @classmethod
    def create(cls, obj: User) -> "UserSettingsResponse":
        return UserSettingsResponse(
            email=obj.email,
            phone=obj.phone,
            avatar=obj.avatar
        )


class UserCreate(UserSettings):
    username: str
    @field_validator('username')
    @classmethod
    def _validate_username(cls,value:str)->str:
        if len(value) < 2 or len(value) > 20:
            raise USERNAME_INCORRECT_FORMAT
        return value

    password:str
    @field_validator('password')
    @classmethod
    def _validate_password(cls,value:str)->str:
        if (
            sum(c.isupper() for c in value) < 1
        ) or (
            sum(c.isdigit() for c in value) < 1
        ) or (
            sum(not c.isalnum() for c in value) < 1
        ) or (
            len(value) < 8
        ):
            raise PASSWORD_INCORRECT_FORMAT
        return value

class UserLogin(BaseModel):
    username:str
    password:str

    @classmethod
    def from_oauth2_form_data(cls,form_data:OAuth2PasswordRequestForm)->"UserLogin":
        return cls(
            username=form_data.username,
            password=form_data.password
        )

class UserPasswordCollection(BaseModel):
    new_password: str
    @field_validator('new_password')
    @classmethod
    def _validate_password(cls,value:str)->str:
        if (
            sum(c.isupper() for c in value) < 1
        ) or (
            sum(c.isdigit() for c in value) < 1
        ) or (
            sum(not c.isalnum() for c in value) < 1
        ) or (
            len(value) < 8
        ):
            raise PASSWORD_INCORRECT_FORMAT
        return value
    old_password: str