from pydantic import BaseModel


class UploadResponseSchema(BaseModel):
    saved_documents: list[str]