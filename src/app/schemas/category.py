from pydantic import BaseModel
from uuid import UUID

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: UUID

    class Config:
        orm_mode = True
