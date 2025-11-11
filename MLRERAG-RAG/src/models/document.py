from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .chunk import Chunk

class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    source_url: Mapped[str] = mapped_column(nullable=False)
    published_at: Mapped[datetime] = mapped_column(nullable=False)

    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document", default_factory=list)