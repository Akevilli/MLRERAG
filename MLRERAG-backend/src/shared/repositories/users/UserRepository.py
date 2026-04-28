from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..BaseRepository import BaseRepository

from src.shared.databases.postgres.models import User


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
            query = (select(User).where(User.username == username)
                     .options(selectinload(User.chats)))

            result = await self._session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        query = (select(User).where(User.email == email)).options(selectinload(User.chats))

        result = await self._session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_id(self, id: UUID) -> Optional[User]:
        query = select(User).where(User.id == id).options(selectinload(User.chats))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()