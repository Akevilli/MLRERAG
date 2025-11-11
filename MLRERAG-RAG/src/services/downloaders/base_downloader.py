from abc import ABC, abstractmethod

from src.api.schemas import UploadSchema

from .schemas import DocumentInfo


class Downloader(ABC):
    @abstractmethod
    def download(self, upload_data: UploadSchema) -> list[DocumentInfo]:
        pass