from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateMessageSchema(BaseModel):
    content: str
    is_users: bool
    chat_id: UUID


class MessageSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    content: str
    is_users: bool


class MessagePaginationSchema(BaseModel):
    items: list[MessageSchema]
    page: int
    total: int