from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from ..BaseRepository import BaseRepository

from src.models import User


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str, session: Session) -> User | None:
            query = (select(User).where(User.username == username)
                     .options(selectinload(User.chats)))

            result = session.execute(query)
            return result.scalar_one_or_none()

    def get_by_email(self, email: str, session: Session) -> User | None:
        query = (select(User).where(User.email == email)).options(selectinload(User.chats))

        result = session.execute(query)
        return result.scalar_one_or_none()


    def get_by_id(self, id: UUID, session: Session) -> Optional[User]:
        query = select(User).where(User.id == id).options(selectinload(User.chats))
        result = session.execute(query)
        return result.scalar_one_or_none()