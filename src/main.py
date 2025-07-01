import random
import os

from fastapi import FastAPI, Depends, BackgroundTasks
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from src.config.core.database_helper import database_helper
from src.services.parser_and_save_menu import MenuService
from src.dependencies.service import get_menu_service

app = FastAPI()

class URL(BaseModel):
    url: str

@app.post("/parse-data/")
async def parse_data(
    url: URL,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(database_helper.session_depends),
    menu_service: MenuService = Depends(get_menu_service),
):
    background_tasks.add_task(
        menu_service.add_position_to_menu,
        session,
        url.url
    )
    return {"message": "task started"}