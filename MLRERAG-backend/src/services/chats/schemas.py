from uuid import UUID

from pydantic import BaseModel


class CreateChatSchema(BaseModel):
    title: str
    owner_id: UUID