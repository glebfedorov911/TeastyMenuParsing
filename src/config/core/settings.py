from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os


class DataBaseSettings(BaseModel):
    url: str = os.getenv("DATABASE_URL")
    echo: bool = os.getenv("DATABASE_ECHO") == "True"

class Settings(BaseSettings):
    database_settings: DataBaseSettings = DataBaseSettings()

settings = Settings()