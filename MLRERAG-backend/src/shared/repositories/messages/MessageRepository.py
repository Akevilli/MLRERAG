from uuid import UUID
from typing import Tuple, Literal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.databases.postgres.models import Message
from ..BaseRepository import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_messages_by_chat_id(
            self,
            chat_id: UUID,
            page: int,
            page_size: int,
            sort: Literal["asc", "desc"]
    ) -> Tuple[int, list[Message]]:
        query = select(Message).where(Message.chat_id == chat_id)
        amount_query = select(func.count()).select_from(query.subquery())
        query = (query
            .offset(page * page_size)
            .order_by(Message.created_at.desc() if sort == "desc" else Message.created_at.asc())
            .limit(page_size)
        )

        total = (await self._session.execute(amount_query)).scalar_one()
        result = (await self._session.execute(query)).scalars().all()
        return total, list(result)
