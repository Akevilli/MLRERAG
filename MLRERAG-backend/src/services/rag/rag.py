import requests
from sqlalchemy.orm import Session

from src.core import settings
from src.api.schemas import RAGQuerySchema
from src.services import ChatService, CreateChatSchema, MessageService, CreateMessageSchema
from src.models import Message
from .schemas import MessageSchema, RAGResponseSchema, ChatSchema, RAGRServiceResponseSchema


class RAGService:
    def __init__(
        self,
        chat_service: ChatService,
        message_service: MessageService,
    ):
        self.__chat_service = chat_service
        self.__message_service = message_service

    def generate_answer(
        self,
        query: RAGQuerySchema,
        user_credentials: dict,
        session: Session
    ) -> RAGRServiceResponseSchema | dict:
        messages: list[Message] = []

        if query.chat_id is not None:
            messages = self.__message_service.get_latest_chat_messages(query.chat_id, session)

        transformed_messages = [MessageSchema(content=message.content, is_users=message.is_users) for message in messages]
        transformed_messages.append(MessageSchema(content=query.prompt, is_users=True))

        response = requests.post(
            url=settings.RAG_SERVICE_URL + "/rag/generate_answer",
            json={"messages": [message.model_dump() for message in transformed_messages]},
        )

        if response.status_code != 200:
            return response.json()

        result = RAGResponseSchema(**response.json())

        if query.chat_id is not None:
            chat = self.__chat_service.get_by_id(query.chat_id, session)
        else:
            chat = self.__chat_service.create(CreateChatSchema(
                title=" ".join(result.answer.split()[:3]),
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
        return RAGRServiceResponseSchema(
            answer=result.answer,
            documents=result.documents,
            chat=ChatSchema.model_validate(chat)
        )

