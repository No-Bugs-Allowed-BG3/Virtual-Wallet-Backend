from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey
from app.persistence.users.users import User
from app.persistence.db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    
