import random
import shutil

from fastapi import (
    FastAPI, Depends, BackgroundTasks,
    UploadFile, File, Body
)
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from src.config.core.database_helper import database_helper
from src.services.parser_and_save_menu import MenuService
from src.dependencies.service import get_menu_service
from src.qr.qr_cv2 import QRReaderCV2
from src.config.core.settings import settings

app = FastAPI()

class URL(BaseModel):
    url: str


@app.post("/parse-data-url/")
async def parse_data_url(
        background_tasks: BackgroundTasks,
        url: URL,
        session: AsyncSession = Depends(database_helper.session_depends),
        menu_service: MenuService = Depends(get_menu_service),
):
    background_tasks.add_task(
        menu_service.add_position_to_menu,
        session,
        url.url
    )
    return {"message": "task started"}

@app.post("/parse-data-qr/")
async def parse_data_qr(
    background_tasks: BackgroundTasks,
    qr_code: UploadFile,
    session: AsyncSession = Depends(database_helper.session_depends),
    menu_service: MenuService = Depends(get_menu_service),
):
    qr = QRReaderCV2()
    qr_name = f"temp_qr_code_{random.randint(1, 999999)}"
    qr_path = f"{settings.file_settings.path_qr}{qr_name}.png"
    with open(qr_path, "wb") as buffer:
        shutil.copyfileobj(qr_code.file, buffer)
    url = qr.read(qr_path)

    background_tasks.add_task(
        menu_service.add_position_to_menu,
        session,
        url
    )
    return {"message": "task started"}