from typing import List

from .paper_repository import PaperRepository
from .lib import arxiv_metadata_to_paper_record_create_dto, arxiv_metadata_to_paper_record_update_dto
from src.shared.schemas import ArxivMetadata


class PaperService:
    """Service layer for paper-related business operations.

    Manages the registration and lifecycle of paper records during
    the ingestion pipeline.

    Attributes:
        _paper_repository: Repository for paper persistence operations.
    """

    def __init__(self, paper_repository: PaperRepository):
        """Initializes the PaperService with a paper repository.

        Args:
            paper_repository: Repository for database operations on paper records.
        """
        self._paper_repository = paper_repository

    async def register_papers(self, papers_metadata: List[ArxivMetadata]) -> List[ArxivMetadata]:
        """Registers new papers for processing, returning only unprocessed ones.

        Creates 'in_progress' records for papers not yet in the database,
        allowing the pipeline to track which papers are being processed.

        Args:
            papers_metadata: List of ArxivMetadata for papers to register.

        Returns:
            List of ArxivMetadata for papers that were newly registered
            (excludes papers already being processed).
        """
        new_papers = [arxiv_metadata_to_paper_record_create_dto(metadata) for metadata in papers_metadata]
        reserved_papers = await self._paper_repository.create_many(new_papers)
        unloaded_paper_ids = {reserved_paper.arxiv_id for reserved_paper in reserved_papers}

        return [paper for paper in papers_metadata if paper.arxiv_id in unloaded_paper_ids]

    async def delete_papers(self, paper_ids: List[str]):
        """Deletes paper records by their arXiv IDs.

        Args:
            paper_ids: List of arXiv IDs to delete.
        """
        for paper_id in paper_ids:
            await self._paper_repository.delete_by_arxiv_id(paper_id)

    async def mark_as_loaded(self, papers_metadata: List[ArxivMetadata]):
        update_dtos = [arxiv_metadata_to_paper_record_update_dto(paper, "completed") for paper in papers_metadata]
        entities = await self._paper_repository.get_by_arxiv_ids([paper.arxiv_id for paper in papers_metadata])

        for entity, update_dto in zip(entities, update_dtos):
            self._paper_repository.update(entity, update_dto)