from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageSchema(BaseModel):
    content: str
    is_users: bool


class ChatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class RAGResponseSchema(BaseModel):
    answer: str
    documents: str


class RAGRServiceResponseSchema(RAGResponseSchema):
    chat: ChatSchema