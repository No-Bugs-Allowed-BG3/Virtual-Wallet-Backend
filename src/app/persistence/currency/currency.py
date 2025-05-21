from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Currency(Base):
    __tablename__ = "currency"

    id = Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code = Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name = Mapped[str] = mapped_column(String, nullable=False)