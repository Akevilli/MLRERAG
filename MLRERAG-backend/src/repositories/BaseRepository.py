from typing import Type, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.models import Base


class BaseRepository[T: Base]:
    def __init__(self, model: Type[Base]):
        self.__model: Type[Base] = model

    def get_by_id(self, id: UUID, session: Session) -> Optional[T]:
        query = select(self.__model).where(self.__model.id == id)
        result = session.execute(query)
        return result.scalar_one_or_none()

    def create(self, entity: T, session: Session) -> T:
        session.add(entity)
        session.flush()
        session.refresh(entity)

        return entity

    def update(self, entity: T, updated_data: BaseModel) -> T:

        for key, value in updated_data.model_dump().items():
            setattr(entity, key, value)

        return entity

    def delete(self, entity: T, session: Session):
        session.delete(entity)
