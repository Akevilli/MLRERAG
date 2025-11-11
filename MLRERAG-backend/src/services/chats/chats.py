from uuid import UUID

from sqlalchemy.orm import Session

from src.repositories import ChatRepository
from src.models import Chat
from .schemas import CreateChatSchema


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository
    ):
        self.__chat_repository = chat_repository

    def get_by_id(self, chat_id: UUID, session: Session) -> Chat:
        return self.__chat_repository.get_by_id(chat_id, session)

    def create(self, chat_schema: CreateChatSchema, session: Session,) -> Chat:
        chat = Chat(**chat_schema.model_dump())
        chat = self.__chat_repository.create(chat, session)
        return chat