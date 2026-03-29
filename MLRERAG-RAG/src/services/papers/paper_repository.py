from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.database.models.paper import Paper
from .schemas import PaperRecordCreateDTO, PaperRecordUpdateDTO


class PaperRepository:
    """Repository for managing Paper entity persistence operations.

    Provides async CRUD operations for paper records using SQLAlchemy async sessions.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: An async SQLAlchemy session for database operations.
        """
        self._session = session

    async def get_by_id(self, paper_id: UUID) -> Optional[Paper]:
        """Retrieve a paper record by its primary key UUID.

        Args:
            paper_id: The UUID primary key of the paper to retrieve.

        Returns:
            The Paper ORM object if found, otherwise None.
        """
        return await self._session.get(Paper, paper_id)

    async def create_many(self, create_schemas: List[PaperRecordCreateDTO]) -> List[Paper]:
        """Atomically insert multiple paper records with conflict handling.

        Attempts to insert all provided paper records. If a record with the same
        (arxiv_id, version) combination already exists, it is silently ignored
        via ON CONFLICT DO NOTHING. Commits immediately so other processes can
        see the 'in_progress' status.

        Args:
            create_schemas: List of DTOs containing paper data to insert.

        Returns:
            List of newly created Paper ORM objects (excluding any that already existed).
        """
        if not create_schemas:
            return []

        values = [s.model_dump() for s in create_schemas]

        stmt = (
            insert(Paper)
            .values(values)
            .on_conflict_do_nothing(index_elements=['arxiv_id', 'version'])
            .returning(Paper)
        )

        result = await self._session.execute(stmt)
        reserved_papers = list(result.scalars().all())

        await self._session.commit()

        return reserved_papers

    async def update(self, entity: Paper, update_dto: PaperRecordUpdateDTO) -> Paper:
        """Update an existing Paper entity with partial data from a DTO.

        Applies only the fields that are explicitly set in the update_dto
        (uses exclude_unset=True). Commits immediately and refreshes the entity.

        Args:
            entity: The Paper ORM object to update (must be attached to session).
            update_dto: DTO containing the fields to update.

        Returns:
            The updated Paper ORM object with refreshed database state.
        """
        update_data = update_dto.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(entity, key, value)

        return entity

    async def get_by_arxiv_ids(self, arxiv_ids: List[str]) -> List[Paper]:
        """Fetch all paper records matching the provided arxiv_ids.

        Queries existing paper records by their arxiv_id values. Useful for
        pre-filtering or checking the status of papers before processing.

        Args:
            arxiv_ids: List of arxiv_id strings to search for.

        Returns:
            List of Paper ORM objects matching any of the provided arxiv_ids.
        """
        stmt = select(Paper).where(Paper.arxiv_id.in_(arxiv_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, entity: Paper) -> None:
        """Remove a paper record from the database.

        Deletes the provided entity and commits the transaction immediately.

        Args:
            entity: The Paper ORM object to delete (must be attached to session).

        Returns:
            None
        """
        await self._session.delete(entity)

