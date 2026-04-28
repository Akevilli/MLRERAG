from uuid import UUID
from typing import Tuple, Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..BaseRepository import BaseRepository
from src.shared.databases.postgres.models import Chat


class ChatRepository(BaseRepository[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Chat, session)

    async def get_chats(
            self,
            page: int,
            page_size: int,
            sort: Literal["asc", "desc"],
            user_id: UUID
    ) -> Tuple[int, list[Chat]]:
        query = select(Chat).where(Chat.owner_id == user_id)
        amount_query = select(func.count()).select_from(query.subquery())
        query = (query
             .offset(page * page_size)
             .limit(page_size)
             .order_by(Chat.updated_at.desc() if sort == "desc" else Chat.updated_at.asc())
        )

        amount = (await self._session.execute(amount_query)).scalar_one()
        result = (await self._session.execute(query)).scalars().all()
        return amount, list(result)