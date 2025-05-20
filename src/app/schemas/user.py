from pydantic import BaseModel

from app.crud.users.user import User


class UserResponse(BaseModel):
    id: int
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
    id: int
    username: str
    password: str
