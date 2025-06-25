import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.core.base import Base

class Ingredient(Base):
    __tablename__ = "restoran_ingredients"

    name: Mapped[str] = mapped_column(String(500), nullable=False)

    id_rest: Mapped[uuid.UUID] = mapped_column(ForeignKey("restoran_restaurant.id"), nullable=True)

    def __repr__(self):
        return f"<Ingredient(name='{self.name}')>"
