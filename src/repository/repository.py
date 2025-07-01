from abc import ABC
from typing import TypeVar, Type, Sequence, Tuple, Dict, Generic

from sqlalchemy import select, Result, Select, func, and_
from sqlalchemy.orm import RelationshipProperty


ModelType = TypeVar('ModelType')
SessionType = TypeVar('SessionType')

class BaseRepository(Generic[ModelType, SessionType], ABC):


    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, session: SessionType, id_: str) -> ModelType:
        stmt = select(self.model).where(self.model.id==id_)
        records = await self._get_result(session, stmt)
        return self._get_first_record(records)

    async def get_all(
            self, session: SessionType, offset: int = 0, limit: int = 10
    ) -> Tuple[int, Sequence[ModelType]]:
        stmt = select(self.model).offset(offset).limit(limit)
        stmt_count = select(func.count()).select_from(self.model)
        records = await self._get_result(session, stmt)
        count_records: Result = await session.execute(stmt_count)
        return count_records.scalar_one(), records

    async def add(self, session: SessionType, data_add: Dict[str, any]) -> ModelType:
        found, instance = await self._get_if_already_exists(session, data_add)
        if found:
            return instance

        instance = self.model(**data_add)
        session.add(instance)
        await self._commit_and_refresh_session(session, instance)
        return instance

    async def update(self, session: SessionType, id_: str, data_update: Dict[str, any]) -> ModelType:
        instance = self.get_by_id(session, id_)
        updated_instance = self._update_data_in_instance(instance, data_update)
        await self._commit_and_refresh_session(session, instance)
        return updated_instance

    async def delete(self, session: SessionType, id_: str) -> None:
        instance = self.get_by_id(session, id_)
        await session.delete(instance)
        await self._commit_and_refresh_session(session)

    @staticmethod
    async def _get_result(session: SessionType, stmt: Select) -> Sequence[ModelType]:
        result: Result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    def _get_first_record(records: Sequence[ModelType]) -> ModelType:
        if records:
            return records[0]
        raise ValueError("Not found records")

    @staticmethod
    async def _commit_and_refresh_session(session: SessionType, instance: ModelType | None = None) -> None:
        await session.commit()
        if instance is not None:
            await session.refresh(instance)

    @staticmethod
    def _update_data_in_instance(instance: ModelType, updated_data: Dict[str, any]) -> ModelType:
        for key, value in updated_data.items():
            if value is not None:
                setattr(instance, key, value)
        return instance

    async def _get_if_already_exists(
            self, session: SessionType, data_add: Dict[str, any]
    ) -> Tuple[bool, ModelType | None]:
        conditions = self._get_all_conditions(data_add)
        stmt = select(self.model).where(and_(*conditions))
        result = await session.execute(stmt)
        if instance := result.scalars().first():
            return True, instance
        return False, None

    def _get_all_conditions(self, data_add: dict):
        conditions = []
        for field, value in data_add.items():
            if not hasattr(self.model, field):
                continue

            attr = getattr(self.model, field)
            if isinstance(attr.property, RelationshipProperty):
                continue

            conditions.append(attr == value)

        return conditions