from uuid import UUID

from sqlalchemy.orm import Session

from src.services.chats import ChatService
from src.repositories import MessageRepository
from src.models import Message
from .schemas import CreateMessageSchema, MessageSchema, MessagePaginationSchema


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        chat_service: ChatService,
    ):
        self.__message_repository = message_repository
        self.__chat_service = chat_service


    def get_latest_chat_messages(
        self,
        chat_id: UUID,
        user_credentials: dict,
        session: Session
    ) -> MessagePaginationSchema:
        chat = self.__chat_service.get_by_id(chat_id, user_credentials, session)
        total, messages = self.__message_repository.get_latest_messages_by_chat_id(chat.id, session)
        return MessagePaginationSchema(
            total=total,
            items=[MessageSchema.model_validate(message) for message in messages],
            page=0
        )


    def create(self, message_schema: CreateMessageSchema, session: Session) -> Message:
        message = Message(**message_schema.model_dump())
        message = self.__message_repository.create(message, session)
        return message
