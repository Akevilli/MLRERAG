from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from ..BaseRepository import BaseRepository
from src.models import Chat


class ChatRepository(BaseRepository):
    def __init__(self):
        super().__init__(Chat)

    def get_chats(self, page: int, user_id: UUID, session: Session) -> list[Chat]:
        query = (select(Chat)
            .where(Chat.owner_id == user_id)
            .offset(page*10)
            .limit(10)
            .order_by(Chat.updated_at.desc())
        )

        result = session.execute(query)
        return result.scalars().all()