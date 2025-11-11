from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core import settings
from src.models import Message
from ..BaseRepository import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(Message)

    def get_latest_messages_by_chat_id(self, chat_id: UUID, session: Session) -> list[Message]:
        query = (select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(settings.CONTEXT_WINDOW)
        )

        result = session.execute(query)
        return result.scalars().all()
