from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)

from typing import AsyncGenerator

from src.config.core.settings import settings


class DataBaseHelper:
    AUTOFLUSH = False
    AUTOCOMMIT = False
    EXPIRE_ON_COMMIT = False

    def __init__(self, url: str, echo: bool):
        self.engine = create_async_engine(url, echo=echo)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autocommit=self.AUTOCOMMIT,
            expire_on_commit=self.EXPIRE_ON_COMMIT,
            autoflush=self.AUTOFLUSH,
        )

    async def session_depends(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            yield session

database_helper = DataBaseHelper(
    url=settings.database_settings.url,
    echo=settings.database_settings.echo
)