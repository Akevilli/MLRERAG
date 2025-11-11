import requests
from sqlalchemy.orm import Session

from src.core import settings
from src.api.schemas import RAGQuerySchema
from src.services import ChatService, CreateChatSchema, MessageService, CreateMessageSchema
from src.models import Message
from .schemas import MessageSchema, RAGResponseSchema, ChatSchema


class RAGService:
    def __init__(
        self,
        chat_service: ChatService,
        message_service: MessageService,
    ):
        self.__chat_service = chat_service
        self.__message_service = message_service

    def generate_answer(self, query: RAGQuerySchema, user_credentials: dict, session: Session) -> RAGResponseSchema:
        messages: list[Message] = []

        if query.chat_id is not None:
            messages = self.__message_service.get_latest_chat_messages(query.chat_id, session)

        transformed_messages = [MessageSchema(content=message.content, is_users=message.is_users) for message in messages]
        transformed_messages.append(MessageSchema(content=query.content, is_users=query.is_users))

        response = requests.post(
            url=settings.RAG_SERVICE_URL + "/rag",
            json={"messages": [message.model_dump() for message in transformed_messages]},
        )

        result = RAGResponseSchema(**response.json())

        if query.chat_id is not None:
            chat = self.__chat_service.get_by_id(query.chat_id, session)
        else:
            chat = self.__chat_service.create(CreateChatSchema(
                title="".join(result.answer.split()[:3]),
                owner_id=user_credentials["user_id"],
            ), session)

        self.__message_service.create(CreateMessageSchema(
            content=query.prompt,
            chat_id=chat.id,
            is_users=True
        ), session)
        self.__message_service.create(CreateMessageSchema(
            content=result.answer,
            chat_id=chat.id,
            is_users=False
        ), session)

        return RAGResponseSchema(
            **result.model_dump(),
            chat=ChatSchema(
                id=chat.id,
                title=chat.title,
                owner_id=chat.owner_id,
                created_at=chat.created_at,
                updated_at=chat.updated_at
            )
        )

