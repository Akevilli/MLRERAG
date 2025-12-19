from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ..BaseRepository import BaseRepository
from src.models import Chat


class ChatRepository(BaseRepository):
    def __init__(self):
        super().__init__(Chat)

    def get_chats(self, page: int, user_id: UUID, session: Session) -> (int, list[Chat]):
        query = select(Chat).where(Chat.owner_id == user_id)
        amount_query = select(func.count()).select_from(query.subquery())
        query = (query
             .offset(page * 10)
             .limit(10)
             .order_by(Chat.updated_at.desc())
        )

        amount = session.execute(amount_query).scalar_one()
        result = session.execute(query).scalars().all()
        return amount, result