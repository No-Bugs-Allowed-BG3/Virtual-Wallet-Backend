from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.persistence.users.users import User
from app.persistence.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class UserDevice(Base):
    __tablename__ ="user_devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    device_id: Mapped[str] = mapped_column(nullable=False,unique=True)
    user_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="owned_devices")