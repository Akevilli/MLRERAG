from typing import List

from pydantic import BaseModel

from src.shared.schemas import PaperUploadDTO


class PaperUploadRequest(BaseModel):
    id_list: List[str]

    def to_dto(self) -> PaperUploadDTO:
        return PaperUploadDTO(id_list=self.id_list)


class PaperUploadResponse(BaseModel):
    saved_documents: List[str]