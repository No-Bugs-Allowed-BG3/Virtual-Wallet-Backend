import uuid
from pydantic import BaseModel
from uuid import UUID

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    name: str
    user_id: uuid.UUID

class CategoryRead(CategoryBase):
    id: UUID
    name: str
    user_id: UUID | None = None
    is_deleted: bool
    is_default: bool

    class Config:
        orm_mode = True
