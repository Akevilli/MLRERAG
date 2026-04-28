from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.services.rag import RAGRequestDTO


class RAGQuerySchema(BaseModel):
    query: str = Field(description="User's query", max_length=5000)
    chat_id: Optional[UUID] = Field(default=None)

    def to_dto(self) -> RAGRequestDTO:
        return RAGRequestDTO(**self.model_dump())