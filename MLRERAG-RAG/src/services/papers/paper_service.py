from typing import List

from .paper_repository import PaperRepository
from .schemas import (
    PaperRecordReadDTO,
    PaperRecordCreateDTO,
    PaperRecordUpdateDTO
)
from src.shared.schemas import ArxivMetadata


class PaperService:
    def __init__(self, paper_repository: PaperRepository):
        self._paper_repository = paper_repository

    async def register_papers(self, papers: List[ArxivMetadata]) -> List[ArxivMetadata]:
        new_papers = [PaperRecordCreateDTO.model_validate(**paper.model_dump()) for paper in papers]
        reserved_papers = await self._paper_repository.create_many(new_papers)
        unloaded_paper_ids = {reserved_paper.arxiv_id for reserved_paper in reserved_papers}

        return [paper for paper in papers if paper.arxiv_id in unloaded_paper_ids]
