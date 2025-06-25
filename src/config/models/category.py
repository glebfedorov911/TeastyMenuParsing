import uuid
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.core.base import Base

class Category(Base):
    __tablename__ = "restoran_category"

    id_category_iiko: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    parrent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("restoran_category.id"), nullable=True)

    parrent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], backref="children")

    des: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    show: Mapped[bool] = mapped_column(Boolean, default=True)

    photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    id_rest: Mapped[uuid.UUID] = mapped_column(ForeignKey("restoran_restaurant.id"), nullable=False)

    def __repr__(self):
        return f"<Category(name='{self.name}', id='{self.id}')>"
