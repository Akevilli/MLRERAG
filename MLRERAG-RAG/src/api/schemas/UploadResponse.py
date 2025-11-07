from pydantic import BaseModel


class UploadResponse(BaseModel):
    saved_documents: list[str]