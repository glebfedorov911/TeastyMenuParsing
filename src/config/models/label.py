import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.core.base import Base

class Label(Base):
    __tablename__ = "restoran_label"

    name: Mapped[str] = mapped_column(String(500), nullable=False)

    id_rest: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restaurant.id"), nullable=True)

    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Путь до изображения

    dishes = relationship("restoran_dish", secondary="dish_label_association", back_populates="labels")

    def __repr__(self):
        return f"<Label(name='{self.name}')>"
