from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..BaseRepository import BaseRepository
from src.shared.databases.postgres.models import RefreshToken


class RefreshTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
    
    async def get_active_token(self, owner_id: UUID) -> list[RefreshToken]:
        query = select(RefreshToken).where((RefreshToken.owner_id == owner_id) & (RefreshToken.is_revoked == False))

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_active_by_user_id_and_token(self, user_id: UUID, token: UUID) -> RefreshToken | None:
        query = select(RefreshToken).where(
            (RefreshToken.id == token) &
            (RefreshToken.owner_id == user_id) &
            (RefreshToken.is_revoked == False)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()