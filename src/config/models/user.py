from typing import Optional
from datetime import datetime
import uuid
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Enum

from src.config.core.base import Base


class RoleEnum(str, enum.Enum):
    client = 'client'
    administrator = 'administrator'
    employe = 'employe'

class User(Base):
    __tablename__ = "accounts_useraccounts"

    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    patronymic_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    phone: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)

    avatar: Mapped[Optional[str]] = mapped_column(nullable=True)
    birthday: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    anonim_user_obj_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts_anonimuser.id"), nullable=True)
    anonim_user = relationship("AnonimUser", back_populates="users")

    role: Mapped[Optional[RoleEnum]] = mapped_column(String, nullable=True)

    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    in_consideration: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

from src.config.models.anonim_user import AnonimUser