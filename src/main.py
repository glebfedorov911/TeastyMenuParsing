from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.config.core.database_helper import database_helper
from src.config.models.restaurant import Restaurant
from src.config.models.user import User
from src.config.models.dish import Dish, Ingredient
from src.config.core.settings import settings
from src.services.parser_and_save_menu import MenuService
import random


app = FastAPI()

@app.get("/")
async def root(session: AsyncSession = Depends(database_helper.session_depends)):
    # phone = f"+7{random.randint(100000000, 1000000000)}"
    # administrator = User(
    #     phone=phone,
    #     role="administrator"
    # )

    restaraunt = Restaurant(
        name='TEST123',
        legal_person="TEST123",
        using_iiko=False,
        using_rkeeper=False,
        using_postpaid=False,
        administartor_id="5fdf78b0-a926-4311-92a8-37e8f0f43a59"
    )

    session.add(restaraunt)
    await session.commit()
    await session.refresh(restaraunt)

    # name = "test_new_ingredient_from_fastapi"
    # id_rest_id = "69580c2b-66c4-40c7-a98b-8fdb2d4bb078"
    # ingredient = Ingredient(name=name, id_rest_id=id_rest_id)
    # session.add(ingredient)
    # await session.commit()
    # await session.refresh(ingredient)
    #
    # stmt = select(Ingredient)
    # result = await session.execute(stmt)
    # ingredients = result.scalars().all()
    # for ingredient in ingredients:
    #     print(ingredient.name)

    return {"message": "Hello world"}

from pydantic import BaseModel
class Sch(BaseModel):
    url: str

@app.post("/parse-data/")
async def parse_data(url: Sch, session: AsyncSession = Depends(database_helper.session_depends)):
    from src.httpclient.httpx_http_client import HttpxHttpClient
    from src.ai.chatgpt_ai import ChatGptAI
    from src.parser.parser_playwright import PlaywrightParser

    client = HttpxHttpClient()
    ai = ChatGptAI(token, client)

    service = MenuService(ai, PlaywrightParser)
    await service.add_position_to_menu(session, url.url)