from uuid import UUID

from pydantic import BaseModel


class CreateMessageSchema(BaseModel):
    content: str
    is_users: bool
    chat_id: UUID