from uuid import UUID
from typing import Literal

from pydantic import BaseModel, Field


class BaseMessageDTO(BaseModel):
    text: str = Field(description="Text of the message.")
    type: Literal["assistant", "user", "tool"] = Field(description="Type of the message.")
    chat_id: UUID = Field(description="Chat identifier of the message.")

class MessageViewDTO(BaseMessageDTO):
    id: UUID = Field(description="Identifier of the message.")

class CreateMessageDTO(BaseMessageDTO):
    pass