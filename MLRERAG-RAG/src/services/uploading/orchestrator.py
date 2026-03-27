from src.shared.schemas import (
    PaperUploadDTO,
    UploadedPaperDTO,
    PaperIngestionDTO
)
from .arxiv_provider import ArxivProvider


class PaperIngestionService:
    def __init__(self, arxiv_provider: ArxivProvider):
        self._arxiv_provider = arxiv_provider

    async def process(self, upload_dto: PaperUploadDTO) -> UploadedPaperDTO:
        arxiv_metadata = self._arxiv_provider.get_metadata(upload_dto.id_list)

        # Check uploading

        async for paper_id, paper_bytes in self._arxiv_provider.download(upload_dto.id_list):
            pass
