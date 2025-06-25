from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os


class DataBaseSettings(BaseModel):
    url: str = os.getenv("DATABASE_URL")
    echo: bool = os.getenv("DATABASE_ECHO") == "True"

class FileSettings(BaseSettings):
    path_create_upload_fir: str = "src/statis/uploads/"
    path_logo: str = path_create_upload_fir + "logo/"
    path_avatar: str = path_create_upload_fir + "avatar/"
    path_img: str = path_create_upload_fir + "img/"
    path_dish: str = path_create_upload_fir + "dish/"

class Settings(BaseSettings):
    database_settings: DataBaseSettings = DataBaseSettings()
    file_settings: FileSettings = FileSettings()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for dirpath in self.file_settings.model_dump():
            os.makedirs(dirpath, exist_ok=True)

settings = Settings()