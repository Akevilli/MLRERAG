from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RAGQuerySchema(BaseModel):
    prompt: str = Field(..., max_length=5000)
    chat_id: Optional[UUID] = Field(default=None)