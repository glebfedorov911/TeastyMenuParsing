import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.core.base import Base
from src.config.models.dish import dish_ingredient_association


class Ingredient(Base):
    __tablename__ = "restoran_ingredients"

    name: Mapped[str] = mapped_column(String(500), nullable=False)

    id_rest: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restoran_restaurant.id"), nullable=True)

    dishes = relationship("Dish", secondary=dish_ingredient_association, back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient(name='{self.name}')>"

from src.config.models.dish import Dish
