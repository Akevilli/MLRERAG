from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core import retry_strategy
from src.repositories import ChatRepository
from src.models import Chat
from .schemas import ChatPaginationSchema, CreateChatSchema, ChatSchema


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository
    ):
        self.__chat_repository = chat_repository


    @retry_strategy
    def get_by_id(self, chat_id: UUID, user_credentials: dict, session: Session) -> Chat:
        chat = self.__chat_repository.get_by_id(chat_id, session)

        if str(chat.owner_id) != user_credentials['user_id']:
            raise HTTPException(status_code=403, detail="you don't have permission to access this chat.")

        return chat


    @retry_strategy
    def get_chats(self, page: int, user_credentials: dict, session: Session) -> ChatPaginationSchema:
        total, chats = self.__chat_repository.get_chats(page, user_credentials["user_id"], session)
        return ChatPaginationSchema(total=total, items=[ChatSchema.model_validate(chat) for chat in chats], page=page)


    @retry_strategy
    def create(self, chat_schema: CreateChatSchema, session: Session) -> Chat:
        chat = Chat(**chat_schema.model_dump())
        chat = self.__chat_repository.create(chat, session)
        return chat