from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.shared.databases.postgres import Base


class BaseRepository[T: Base]:
    def __init__(self, model: type[Base], session: AsyncSession):
        self._model = model
        self._session = session

    async def get_by_id(self, id: UUID) -> Optional[T]:
        query = select(self._model).where(self._model.id == id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()

        return entity

    async def update(self, entity: T, updated_data: BaseModel) -> T:

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)

        await self._session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()
