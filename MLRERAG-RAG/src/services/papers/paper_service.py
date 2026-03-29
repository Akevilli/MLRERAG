from typing import List

from .paper_repository import PaperRepository
from .lib import arxiv_metadata_to_paper_record_create_dto
from .schemas import (
    PaperRecordReadDTO,
    PaperRecordCreateDTO,
    PaperRecordUpdateDTO
)
from src.shared.schemas import ArxivMetadata


class PaperService:
    def __init__(self, paper_repository: PaperRepository):
        self._paper_repository = paper_repository

    async def register_papers(self, papers_metadata: List[ArxivMetadata]) -> List[ArxivMetadata]:
        new_papers = [arxiv_metadata_to_paper_record_create_dto(metadata) for metadata in papers_metadata]
        reserved_papers = await self._paper_repository.create_many(new_papers)
        unloaded_paper_ids = {reserved_paper.arxiv_id for reserved_paper in reserved_papers}

        return [paper for paper in papers_metadata if paper.arxiv_id in unloaded_paper_ids]
