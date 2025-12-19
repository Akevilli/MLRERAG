from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core import settings
from src.models import Message
from ..BaseRepository import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(Message)

    def get_latest_messages_by_chat_id(self, chat_id: UUID, session: Session) -> (int, list[Message]):
        query = select(Message).where(Message.chat_id == chat_id)
        amount_query = select(func.count()).select_from(query.subquery())
        query = (query
            .order_by(Message.created_at.desc())
            .limit(settings.CONTEXT_WINDOW)
        )

        total = session.execute(amount_query).scalar_one()
        result = session.execute(query).scalars().all()
        result.reverse()
        return total, result
