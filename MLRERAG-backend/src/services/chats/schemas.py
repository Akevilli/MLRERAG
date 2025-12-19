from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateChatSchema(BaseModel):
    title: str
    owner_id: UUID


class ChatSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    title: str


class ChatPaginationSchema(BaseModel):
    items: list[ChatSchema]
    page: int
    total: int