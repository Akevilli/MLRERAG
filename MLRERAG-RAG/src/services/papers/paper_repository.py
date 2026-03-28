from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.database.models.paper import Paper
from .schemas import PaperRecordReadDTO, PaperRecordCreateDTO, PaperRecordUpdateDTO


class PaperRepository:
    def __init__(self, session: AsyncSession):
        self._session = session


    async def get_by_id(self, paper_id: UUID) -> Optional[Paper]:
        return await self._session.get(Paper, paper_id)

    async def create(self, create_paper_schema: PaperRecordCreateDTO) -> PaperRecordReadDTO:
        new_paper = Paper(**create_paper_schema.model_dump())

        self._session.add(new_paper)
        await self._session.commit()

        await self._session.refresh(new_paper)

        return PaperRecordReadDTO.model_validate(new_paper)

    async def update(self, entity: Paper, update_paper_schema: PaperRecordUpdateDTO) -> PaperRecordReadDTO:
        update_data = update_paper_schema.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(entity, key, value)

        await self._session.commit()
        await self._session.refresh(entity)

        return PaperRecordReadDTO.model_validate(entity)

    async def delete(self, entity: Paper):
        await self._session.delete(entity)
