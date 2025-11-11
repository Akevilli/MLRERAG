from typing import Type, Optional, Any, List

from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.models import Base


class BaseRepository[T: Base]:
    def __init__(self, model: Type[Base]):
        self.__model: Type[Base] = model

    def get_by_id(self, id: Any | List[Any], session: Session) -> Optional[T] | List[T]:
        query = select(self.__model)

        if isinstance(id, list):
            query = query.where(self.__model.id.in_(id))

            result = session.execute(query).scalars().all()
            return result
        else:
            query = query.where(self.__model.id == id)

            result = session.execute(query).scalar_one_or_none()
            return result


    def create(self, entities: list[T], session: Session) -> list[T]:
        session.add_all(entities)
        session.flush()

        for entity in entities:
            session.refresh(entity)

        return entities

    def update(self, entity: T, updated_data: BaseModel) -> T:

        for key, value in updated_data.model_dump().items():
            setattr(entity, key, value)

        return entity

    def delete(self, entity: T, session: Session):
        session.delete(entity)
