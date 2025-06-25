import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.core.base import Base
from src.config.models.dish import dish_label_association


class Label(Base):
    __tablename__ = "restoran_label"

    name: Mapped[str] = mapped_column(String(500), nullable=False)

    id_rest: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restoran_restaurant.id"), nullable=True)

    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    dishes = relationship("Dish", secondary=dish_label_association, back_populates="labels")

    def __repr__(self):
        return f"<Label(name='{self.name}')>"

from src.config.models.dish import Dish
