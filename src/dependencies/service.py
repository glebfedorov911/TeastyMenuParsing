from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.chatgpt_ai import ChatGptAI
from src.dependencies.repository import (
    get_user_repository, get_dish_repository,
    get_category_repository, get_ingredient_repository,
    get_restaurant_repository
)
from src.repository.repository import BaseRepository
from src.config.models.user import User
from src.config.models.dish import Dish, Ingredient
from src.config.models.restaurant import Restaurant
from src.config.models.category import Category
from src.dependencies.ai import get_chatgpt_ai
from src.dependencies.http_client import get_httpx_http_client
from src.services.parser_and_save_menu import MenuService
from src.httpclient.httpx_http_client import HttpxHttpClient
from src.parser.parser_playwright import PlaywrightParser


def get_menu_service(
        user_repo: BaseRepository[User, AsyncSession] = Depends(get_user_repository),
        dish_repo: BaseRepository[Dish, AsyncSession] = Depends(get_dish_repository),
        category_repo: BaseRepository[Category, AsyncSession] = Depends(get_category_repository),
        ingredient_repo: BaseRepository[Ingredient, AsyncSession] = Depends(get_ingredient_repository),
        restaurant_repo: BaseRepository[Restaurant, AsyncSession] = Depends(get_restaurant_repository),
        ai: ChatGptAI = Depends(get_chatgpt_ai),
        http_client: HttpxHttpClient = Depends(get_httpx_http_client),
) -> MenuService:
    return MenuService(
        user_repo=user_repo,
        dish_repo=dish_repo,
        category_repo=category_repo,
        ingredient_repo=ingredient_repo,
        rest_repo=restaurant_repo,
        ai=ai,
        http_client=http_client,
        parser=PlaywrightParser,
    )