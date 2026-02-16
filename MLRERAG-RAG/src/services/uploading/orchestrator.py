from src.shared.schemas import (
    PaperUploadDTO,
    UploadedPaperDTO,
    PaperIngestionDTO
)
from .arxiv_provider import ArxivProvider


class PaperIngestionService:
    def __init__(self, arxiv_provider: ArxivProvider):
        self.__arxiv_provider = arxiv_provider

    def process(self, upload_dto: PaperUploadDTO) -> UploadedPaperDTO:
        paper_ingestion = PaperIngestionDTO()

        paper_ingestion.document_metadata = self.__arxiv_provider.download(upload_dto.id_list)
