from uuid import UUID

from sqlalchemy.orm import Session

from src.repositories import MessageRepository
from src.models import Message
from .schemas import CreateMessageSchema


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
    ):
        self.__message_repository = message_repository

    def get_latest_chat_messages(self, chat_id: UUID, session: Session) -> list[Message]:
        messages = self.__message_repository.get_latest_messages_by_chat_id(chat_id, session)
        return messages

    def create(self, message_schema: CreateMessageSchema, session: Session) -> Message:
        message = Message(**message_schema.model_dump())
        message = self.__message_repository.create(message, session)
        return message
