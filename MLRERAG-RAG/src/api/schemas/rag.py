from typing import List

from pydantic import BaseModel, Field, field_validator
from fastapi import UploadFile, Form

from src.shared.schemas import FileUploadDTO, PDFDTO, PaperUploadDTO, Message, ChatHistory


class PaperUploadRequest(BaseModel):
    id_list: List[str]

    def to_dto(self) -> PaperUploadDTO:
        return PaperUploadDTO(id_list=self.id_list)


class PDFPaperUploadDTO(BaseModel):
    files: List[UploadFile] = Form()

    @field_validator("files")
    def validate_files(cls, files: List[UploadFile]) -> List[UploadFile]:
        valid_files = []

        for file in files:
            if file.content_type == "application/pdf":
                valid_files.append(file)

        return valid_files

    async def to_dto(self) -> FileUploadDTO:
        return FileUploadDTO(
            files=[
                PDFDTO(
                    name=file.filename if file.filename else "",
                    content=await file.read()
                ) for file in self.files
            ]
        )


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