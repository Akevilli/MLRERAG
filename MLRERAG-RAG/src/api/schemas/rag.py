from typing import List

from pydantic import BaseModel, Field

from src.shared.schemas import PaperUploadDTO, Message, ChatHistory


class PaperUploadRequest(BaseModel):
    id_list: List[str]

    def to_dto(self) -> PaperUploadDTO:
        return PaperUploadDTO(id_list=self.id_list)


class PaperUploadResponse(BaseModel):
    loaded: set[str]
    failed: set[str]
    cited: set[str]


class GenerateAnswerRequest(BaseModel):
    messages: List[Message] = Field(description="List of messages.")

    def to_dto(self) -> ChatHistory:
        return ChatHistory(**self.model_dump())


class GenerateAnswerResponse(BaseModel):
    messages: List[Message] = Field(description="List of messages.")