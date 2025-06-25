from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.config.core.database_helper import database_helper
from src.config.models.restaurant import Restaurant


app = FastAPI()

@app.get("/")
async def root(session: AsyncSession = Depends(database_helper.session_depends)):
    stmt = select(Restaurant)
    result = await session.execute(stmt)
    restaurants = result.scalars().all()
    for restaurant in restaurants:
        print(restaurant.name)
    return {"message": "Hello world"}