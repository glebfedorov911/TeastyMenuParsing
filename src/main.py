from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.config.core.database_helper import database_helper
from src.config.models.restaurant import Restaurant
from src.config.models.dish import Dish


app = FastAPI()

@app.get("/")
async def root(session: AsyncSession = Depends(database_helper.session_depends)):
    stmt = select(Dish)
    result = await session.execute(stmt)
    dishes = result.scalars().all()
    for dish in dishes:
        print(dish.name)
    return {"message": "Hello world"}