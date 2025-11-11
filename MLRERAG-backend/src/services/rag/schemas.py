from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    content: str
    is_users: bool


class ChatSchema(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime



class RAGResponseSchema(BaseModel):
    answer: str
    documents: str
    chat: ChatSchema