from src.shared.schemas import (
    PaperUploadDTO,
    UploadedPaperDTO,
    PaperIngestionDTO
)
from .arxiv_provider import ArxivProvider
from ..papers import PaperService


class PaperIngestionService:
    def __init__(
            self,
            arxiv_provider: ArxivProvider,
            paper_service: PaperService,
    ):
        self._arxiv_provider = arxiv_provider
        self._paper_service = paper_service

    async def process(self, upload_dto: PaperUploadDTO) -> UploadedPaperDTO:
        arxiv_metadata = await self._arxiv_provider.get_metadata(upload_dto.id_list)
        unloaded_arxiv_metadata = await self._paper_service.register_papers(arxiv_metadata)

        async for paper_id, paper_bytes in self._arxiv_provider.download([paper.arxiv_id for paper in unloaded_arxiv_metadata]):
            pass
