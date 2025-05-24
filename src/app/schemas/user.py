import uuid

from pydantic import BaseModel,EmailStr
import uuid

from app.persistence.users.users import User


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    hashed_password: str | None = None

    @classmethod
    def create(cls, obj: User) -> "UserResponse":
        return UserResponse(
            id=obj.id,
            username=obj.username,
            hashed_password=obj.password,
        )


class UserCreate(BaseModel):
    username: str
    password: str
    email:EmailStr
