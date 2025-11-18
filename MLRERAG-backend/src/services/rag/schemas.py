from src.services.chats import ChatSchema

from pydantic import BaseModel


class RAGResponseSchema(BaseModel):
    answer: str
    documents: str


class RAGRServiceResponseSchema(RAGResponseSchema):
    chat: ChatSchema