from abc import ABC, abstractmethod

from src.api.schemas import UploadSchema

from src.shared.schemas import DocumentMetadata


class Downloader(ABC):
    @abstractmethod
    def download(self, upload_data: UploadSchema) -> list[DocumentMetadata]:
        pass