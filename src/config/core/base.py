from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from typing import Dict
import uuid


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self) -> Dict[str, any]:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )