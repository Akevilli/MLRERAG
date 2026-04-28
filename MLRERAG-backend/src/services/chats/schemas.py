from uuid import UUID

from pydantic import BaseModel, Field


class ChatBaseDTO(BaseModel):
    title: str = Field(description="Chat title.")
    owner_id: UUID = Field(description="Chat owner's identifier.")

class CreateChatDTO(ChatBaseDTO):
    pass

class ChatViewDTO(ChatBaseDTO):
    id: UUID = Field(description="Chat identifier.")