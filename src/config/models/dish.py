import uuid
from sqlalchemy import String, Float, Boolean, ForeignKey, Integer, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.config.core.base import Base

dish_ingredient_association = Table(
    "restoran_dish_ingredients",
    Base.metadata,
    mapped_column("dish_id", ForeignKey("restoran_dish.id"), primary_key=True),
    mapped_column("ingredient_id", ForeignKey("restoran_ingredients.id"), primary_key=True)
)

dish_label_association = Table(
    "restoran_dish_label",
    Base.metadata,
    mapped_column("dish_id", ForeignKey("restoran_dish.id"), primary_key=True),
    mapped_column("label_id", ForeignKey("restoran_label.id"), primary_key=True)
)


class Dish(Base):
    __tablename__ = "restoran_dish"

    iiko_id_product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rkeeper_id_product: Mapped[int | None] = mapped_column(nullable=True)
    rkeeper_code_product: Mapped[int | None] = mapped_column(nullable=True)
    rkeeper_GUIDString: Mapped[str | None] = mapped_column(String(255), nullable=True)

    id_rest: Mapped[uuid.UUID] = mapped_column(ForeignKey("restoran_restaurant.id"))

    cat_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restoran_category.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    ingredients = relationship("restoran_ingredients", secondary=dish_ingredient_association, back_populates="dishes")
    labels = relationship("restoran_label", secondary=dish_label_association, back_populates="dishes")

    weight: Mapped[float | None] = mapped_column(nullable=True)
    unit: Mapped[str | None] = mapped_column(String(255), nullable=True)

    kall: Mapped[str | None] = mapped_column(String(500), nullable=True)

    cost: Mapped[float | None] = mapped_column(nullable=True)
    cooking_time: Mapped[str | None] = mapped_column(String(500), nullable=True)

    fat_amount: Mapped[float | None] = mapped_column(nullable=True, default=0.0)
    proteins_amount: Mapped[float | None] = mapped_column(nullable=True, default=0.0)
    carbohydrates_amount: Mapped[float | None] = mapped_column(nullable=True, default=0.0)
    energy_amount: Mapped[float | None] = mapped_column(nullable=True, default=0.0)

    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[list[str]] = mapped_column(ARRAY(String(255)), default=list)

    show: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f"<Dish(name='{self.name}', restaurant='{self.id_rest}')>"
