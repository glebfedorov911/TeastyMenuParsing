from typing import Optional
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer

from src.config.core.base import Base


class Restaurant(Base):
    __tablename__ = "restoran_restaurant"

    name: Mapped[str] = mapped_column(String(500))
    legal_person: Mapped[str] = mapped_column(String(500))
    id_iiko: Mapped[Optional[str]] = mapped_column(String(500), default="", nullable=True)
    org_iiko: Mapped[Optional[str]] = mapped_column(String(500), default="", nullable=True)
    id_chanel: Mapped[Optional[str]] = mapped_column(String(500), default="", nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(500), default="", nullable=True)
    using_iiko: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    rkeeper_address: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    rkeeper_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rkeeper_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rkeeper_rest_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rkeeper_cashier_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rkeeper_station_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    using_rkeeper: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    using_postpaid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    administartor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts_useraccounts.id"), nullable=False)

    def __str__(self):
        return f"{self.name} | {self.administartor_id} | {self.id}"