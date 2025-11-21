from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..BaseRepository import BaseRepository
from src.models import RefreshToken


class RefreshTokenRepository(BaseRepository):
    def __init__(self):
        super().__init__(RefreshToken)
    
    def get_active_token(self, owner_id: UUID, session: Session) -> list[RefreshToken]:
        query = select(RefreshToken).where((RefreshToken.owner_id == owner_id) & (RefreshToken.is_revoked == False))

        result = session.execute(query)
        return result.scalars().all()

    def get_active_by_user_id_and_token(self, user_id: UUID, token: UUID, session: Session) -> RefreshToken | None:
        query = select(RefreshToken).where(
            (RefreshToken.id == token) &
            (RefreshToken.owner_id == user_id) &
            (RefreshToken.is_revoked == False)
        )
        result = session.execute(query)
        return result.scalar_one_or_none()