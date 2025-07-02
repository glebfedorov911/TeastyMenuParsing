import random
from urllib.parse import urljoin
from typing import Type
import os
import time
import json
from typing import List

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
        paths = await self._parse_website(path_to_save_parser_files, url)
        if not paths:
            print("Не удалось спарсить данные")
            return

        contents = await self._parse_pages_with_ai(paths)
        if not contents:
            print("AI ничего не смог спарсить")
            return

        administrator = await self._create_administrator(session)
        restaurant = await self._create_restaurant(session, administrator.id, url)

        await self._save_dishes(session, contents, restaurant.id)

    async def _parse_website(self, path_to_save_parser_files: str, url: str) -> List[str]:
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
                print(f"Добавлено url: {href}")

            for i, href in enumerate(hrefs):
                try:
                    await parser.load_page(href)
                    path = await parser.download_html(f"page_{i + 1}.txt")
                    paths.append(path)
                    print(f"Сохраняем страницу {i+1}")
                except:
                    print("Ошибка загрузки страницы")
                    continue

        return paths

    async def _parse_pages_with_ai(self, paths: List[str]) -> List[dict]:
        url_gpt = "https://api.openai.com/v1/chat/completions"
        prompt_system = "Ты парсишь данные"
        contents = []

        for count, path in enumerate(paths):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                file_content = self._clean_html(file_content)
                prompt_user = self._build_prompt_user(file_content)

                print("Запрос номер:", count)
                time.sleep(3)

                result = await self.ai.send_prompt(url_gpt, prompt_system, prompt_user)
                parsed_content = self._extract_content(result)

                if parsed_content:
                    for item in parsed_content:
                        item["img"] = urljoin("https://pizza-romano.qr-cafe.ru/", item.get('img', ""))
                        print("-=" * 10)
                        print(item)
                        contents.append(item)
            except Exception as e:
                print(e)
                print("Ошибка gpt")
                time.sleep(10)

        return contents

    @staticmethod
    def _clean_html(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["style", "script"]):
            tag.decompose()

        return str(soup)

    @staticmethod
    def _build_prompt_user(html: str) -> str:
        return f"""Твоя задача спарсить данные, если они есть такие как
            ингредиенты (если не указаны, то по логике придумай сам), название, описание, цену, картинку (если их несколько то одну возьми), категорию (если нет, то придумай сам по типу товара)
            верни это json'ом ingredients: [], name: "", desc: "", price: "", img: "", category: "",
            если ничего найти не можешь или тебе кажется что это бред, то просто верни пустой json (две фигурные скобки),
            я тебе буду кидать страницу по кусочкам, вот парси отсюда
            {html}"""

    @staticmethod
    def _extract_content(result: dict) -> List[dict]:
        try:
            content = result["choices"][0]["message"]["content"]
            parsed_content = json.loads(content)
            if parsed_content and isinstance(parsed_content, list):
                return parsed_content
        except Exception as e:
            print(f"Ошибка парсинга JSON: {e}")
        return []

    async def _create_administrator(self, session: AsyncSession) -> User:
        user_data = {
            "phone": f"+7{random.randint(100000000, 1000000000)}",
            "password": os.getenv("PASSWORD_HASH_FOR_NEW_USER"),
            "role": "administrator"
        }
        return await self.user_repo.add(session, user_data)

    async def _create_restaurant(self, session: AsyncSession, admin_id: str, url: str) -> Restaurant:
        rest_data = {
            "name": url[8:],
            "legal_person": url[8:],
            "using_iiko": False,
            "using_rkeeper": False,
            "using_postpaid": False,
            "administartor_id": admin_id
        }
        return await self.rest_repo.add(session, rest_data)

    async def _save_dishes(self, session: AsyncSession, contents: List[dict], rest_id: str):
        exists_ingredients = {}
        exists_category = {}
        exists_dish = {}

        for content in contents:
            ingredients = await self._process_ingredients(session, content.get("ingredients", []), rest_id, exists_ingredients)
            category = await self._process_category(session, content.get("category", []), rest_id, exists_category)
            img_url = content.get("img", None)
            path_to_save_photo = await self._download_image(content.get("name", ""), img_url)

            price = content.get("price", "0")
            price = price.split(" ")[0]
            dish_name = content.get("name", f"Неизвестное блюдо_{random.randint(1, 100000)}")
            if dish_name not in exists_dish:
                dish_data = {
                    "id_rest_id": rest_id,
                    "cat_id_id": category.id,
                    "name": dish_name,
                    "description": content.get("desc", ""),
                    "cost": int(price) if price.isdigit() else 0,
                    "show": True,
                    "ingredients": ingredients,
                    "photo": path_to_save_photo,
                }
                dish = await self.dish_repo.add(session, dish_data)
                exists_dish[dish_name] = dish

    async def _process_ingredients(self, session, ingredient_names, rest_id, cache):
        ingredients = []
        for name in ingredient_names:
            if name in cache:
                ingredients.append(cache[name])
                continue

            ingredient_data = {
                "name": name,
                "id_rest_id": rest_id
            }
            ingredient = await self.ingredient_repo.add(session, ingredient_data)
            ingredients.append(ingredient)
            cache[name] = ingredient

        return ingredients

    async def _process_category(self, session, category_name, rest_id, cache):
        if category_name in cache:
            return cache[category_name]

        category_data = {
            "name": category_name,
            "id_rest_id": rest_id
        }
        category = await self.category_repo.add(session, category_data)
        cache[category_name] = category
        return category

    async def _download_image(self, photo_name, img_url: str | None) -> str | None:
        if not img_url:
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'trailers'
        }

        try:
            response = await self.http_client.send_request("GET", img_url, headers=headers)
        except Exception as e:
            print("Неудалось получить фотографию")
            return None
        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            path_to_save_photo = f"{settings.file_settings.path_dish}{photo_name}_{random.randint(1, 100000)}.jpeg"
            with open(path_to_save_photo, 'wb') as file:
                file.write(response.content)
            return path_to_save_photo

        return None