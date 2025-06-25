import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey

from src.config.core.base import Base


class AvatarAnonimUser(Base):
    __tablename__ = "accounts_avataranonimuser"

    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    img: Mapped[str] = mapped_column(String(255))

    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __str__(self):
        return f"{self.title} | {self.img}"


class AnonimUser(Base):
    __tablename__ = "accounts_anonimuser"

    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    session_id: Mapped[str] = mapped_column(String(255), unique=True)
    avatar_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts_avataranonimuser.id"), nullable=True)

    avatar_url: Mapped[str] = mapped_column(String(255))

    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.utcnow)

    def __str__(self):
        return f"{self.session_id} - {self.create_at}"