import random
from urllib.parse import urljoin
from typing import Type
import os
import time

from sqlalchemy.ext.asyncio import AsyncSession
from bs4 import BeautifulSoup

from src.repository.repository import BaseRepository
from src.config.models.user import User
from src.config.models.ingredient import Ingredient
from src.config.models.dish import Dish
from src.config.models.category import Category
from src.config.models.restaurant import Restaurant
from src.parser.parser import Parser
from src.ai.ai import AI
from src.config.core.settings import settings

class MenuService:

    def __init__(
            self,
            ingredient_repo: BaseRepository[Ingredient, AsyncSession],
            category_repo: BaseRepository[Category, AsyncSession],
            rest_repo: BaseRepository[Restaurant, AsyncSession],
            dish_repo: BaseRepository[Dish, AsyncSession],
            ai: AI,
            parser: Type[Parser],
    ):
        self.ingredient_repo = ingredient_repo
        self.category_repo = category_repo
        self.rest_repo = rest_repo
        self.dish_repo = dish_repo
        self.ai = ai
        self.parser = parser
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

        url = "https://api.openai.com/v1/chat/completions"
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
                result = await self.ai.send_prompt(url, prompt_system, prompt_user)
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

            administrator = User(
                phone=f"+7{random.randint(100000000, 1000000000)}",
                role="administrator",
            )
            restaraunt = Restaurant(
                name=url[8:],
                legal_person=url[8:],
                using_iiko=False,
                using_rkeeper=False,
                using_postpaid=False,
                administartor_id=administrator.id
            )
            for content in contents:
                # ingredients: [], name: "", desc: "", price: "", img: "", category: ""
                ...