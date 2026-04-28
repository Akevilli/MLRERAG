from uuid import UUID
from typing import Optional, Literal, List

from src.services.chats import ChatViewDTO

from pydantic import BaseModel, Field


class RAGRequestDTO(BaseModel):
    query: str = Field(description="User's query.")
    chat_id: Optional[UUID] = Field(description="Chat identifier.")

class RAGMessageDTO(BaseModel):
    text: str = Field(description="Text of the message.")
    type: Literal["assistant", "tool"] = Field(description="Type of the message.")

class RAGResponseDTO(BaseModel):
    messages: List[RAGMessageDTO]

class RAGRServiceResponseDTO(RAGResponseDTO):
    chat: ChatViewDTO