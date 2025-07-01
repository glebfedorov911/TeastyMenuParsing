from sqlalchemy.ext.asyncio import AsyncSession

from src.config.models.user import User
from src.config.models.ingredient import Ingredient
from src.config.models.category import Category
from src.config.models.restaurant import Restaurant
from src.config.models.dish import Dish
from src.repository.repository import BaseRepository


def get_user_repository() -> BaseRepository[User, AsyncSession]:
    return BaseRepository(User)

def get_ingredient_repository() -> BaseRepository[Ingredient, AsyncSession]:
    return BaseRepository(Ingredient)

def get_category_repository() -> BaseRepository[Category, AsyncSession]:
    return BaseRepository(Category)

def get_restaurant_repository() -> BaseRepository[Restaurant, AsyncSession]:
    return BaseRepository(Restaurant)

def get_dish_repository() -> BaseRepository[Dish, AsyncSession]:
    return BaseRepository(Dish)