import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.crud.db import Base

if TYPE_CHECKING:
    pass


class User(Base):
    """
    Represents a User entity in the database.

    Attributes:
        id (id): Unique identifier of the user.
        username (str): Username of the user.
        password (str): Password of the user.

    Relationships:
        #pass
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
