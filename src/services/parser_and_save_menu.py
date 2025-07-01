import random
from urllib.parse import urljoin
from typing import Type
import os
import time

from sqlalchemy.ext.asyncio import AsyncSession
from bs4 import BeautifulSoup

from src.repository.repository import BaseRepository
from src.config.models.user import User
from src.config.models.dish import Dish, Ingredient
from src.config.models.category import Category
from src.config.models.restaurant import Restaurant
from src.parser.parser import Parser
from src.ai.ai import AI
from src.config.core.settings import settings
from src.httpclient.http_client import HttpClient

class MenuService:

    def __init__(
            self,
            user_repo: BaseRepository[User, AsyncSession],
            ingredient_repo: BaseRepository[Ingredient, AsyncSession],
            category_repo: BaseRepository[Category, AsyncSession],
            rest_repo: BaseRepository[Restaurant, AsyncSession],
            dish_repo: BaseRepository[Dish, AsyncSession],
            ai: AI,
            parser: Type[Parser],
            http_client: HttpClient,
    ):
        self.user_repo = user_repo
        self.ingredient_repo = ingredient_repo
        self.category_repo = category_repo
        self.rest_repo = rest_repo
        self.dish_repo = dish_repo
        self.ai = ai
        self.parser = parser
        self.http_client = http_client
        self.path_to_save_parser = settings.file_settings.path_parser

    async def add_position_to_menu(self, session: AsyncSession, url: str):
        path_to_save_parser_files = f"{self.path_to_save_parser}{random.randint(100_000, 1_000_000)}"
        os.makedirs(path_to_save_parser_files, exist_ok=True)
        paths = []

        async with self.parser(path_to_save_parser_files, True) as parser:
            await parser.load_page(url)
            elements = await parser.get_element_by_selector("a")
            path = await parser.download_html("page_0.txt")
            paths.append(path)
            hrefs = []
            for i, element in enumerate(elements):
                href = await parser.get_href_from_element(element)
                if not url in href:
                    href = url + href
                hrefs.append(href)

            for i, href in enumerate(hrefs):
                try:
                    await parser.load_page(href)
                    path = await parser.download_html(f"page_{i+1}.txt")
                    paths.append(path)
                except:
                    hrefs.append(href)

        url_gpt = "https://api.openai.com/v1/chat/completions"
        prompt_system = "Ты парсишь данные"

        count_requests = 0
        contents = []
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                soup = BeautifulSoup(file_content, "html.parser")
                for tag in soup(["style", "script"]):
                    tag.decompose()

                file_content = str(soup)

                prompt_user = f"""
                    Твоя задача спарсить данные, если они есть такие как
                    ингредиенты (если не указаны, то по логике придумай сам), название, описание, цену, картинку (если их несколько то одну возьми), категорию (если нет, то придумай сам по типу товара)
                    верни это json'ом ingredients: [], name: "", desc: "", price: "", img: "", category: "",
                    если ничего найти не можешь или тебе кажется что это бред, то просто верни пустой json (две фигурные скобки),
                    я тебе буду кидать страницу по кусочкам, вот парси отсюда
                    {file_content}"""

                if count_requests == 9:
                    break
                count_requests += 1
                print("Запрос номер:", count_requests)
                time.sleep(5)
                result = await self.ai.send_prompt(url_gpt, prompt_system, prompt_user)
                contents = result["choices"][0]["message"]["content"]
                try:
                    import json
                    contents = json.loads(contents)
                    if contents != {}:
                        for content in contents:
                            img = urljoin("https://pizza-romano.qr-cafe.ru/", content.get('img'))
                            print("-="*10)
                            print(content)
                            contents.append(content)
                            # print(f"name = {content.get('name')}")
                            # print(f"desc = {content.get('desc')}")
                            # print(f"ingredients = {content.get('ingredients')}")
                            # print(f"price = {content.get('price')}")
                            # print(f"img = {img}")
                            # print(f"category = {content.get('category')}")
                except:
                    ...
            except:
                print("Ошибка gpt")
                paths.append(path)
                time.sleep(3)

            user_data = {
                "phone": f"+7{random.randint(100000000, 1000000000)}",
                "password": os.getenv("PASSWORD_HASH_FOR_NEW_USER"),
                "role": "administrator"
            }
            administrator = await self.user_repo.add(session, user_data)

            rest_data = {
                "name": url[8:],
                "legal_person": url[8:],
                "using_iiko": False,
                "using_rkeeper": False,
                "using_postpaid": False,
                "administartor_id": administrator.id
            }
            restaurant = await self.rest_repo.add(session, rest_data)

            exists_ingredients = {}
            exists_category = {}
            for content in contents:
                ingredients = []
                for ingredient_name in content.get("ingredients", []):
                    if ingredient := exists_ingredients.get(ingredient_name):
                        ingredients.append(ingredient)
                        continue

                    ingredient_data = {
                        "name": ingredient_name,
                        "id_rest_id": restaurant.id
                    }
                    ingredient = await self.ingredient_repo.add(session, ingredient_data)
                    ingredients.append(ingredient)
                    exists_ingredients[ingredient_name] = ingredient

                category_name = content.get("category", "Неизвестная категория")
                category = exists_category.get(category_name, None)
                if not category:
                    category_data = {
                        "name": category_name,
                        "id_rest_id": restaurant.id
                    }
                    category = await self.category_repo.add(session, category_data)
                    exists_category[category_name] = category

                img_url = content.get("img", None)
                path_to_save_photo = None
                if img_url:
                    response = await self.http_client.send_request("GET", img_url)
                    if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                        path_to_save_photo = f"{settings.file_settings.path_dish}{content.get("name")}_{random.randint(1, 100000)}.jpeg"
                        with open(path_to_save_photo, 'wb') as file:
                            file.write(response.content)

                dish_data = {
                    "id_rest_id": restaurant.id,
                    "cat_id_id": category.id,
                    "name": content.get("name", f"Неизвестное блюдо_{random.randint(1, 100000)}"),
                    "description": content.get("desc", ""),
                    "cost": int(content.get("price", 0)),
                    "show": True,
                    "ingredients": ingredients,
                    "photo": path_to_save_photo,
                }
                dish = await self.dish_repo.add(session, dish_data)