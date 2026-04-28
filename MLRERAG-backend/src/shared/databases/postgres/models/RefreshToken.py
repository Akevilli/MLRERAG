from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base
from src.core import settings

class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    owner_id: Mapped[UUID] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=func.now() + timedelta(days=settings.REFRESH_TOKEN_LIFETIME_DAYS)
    )
    is_revoked: Mapped[bool] = mapped_column(nullable=False, default=False)
