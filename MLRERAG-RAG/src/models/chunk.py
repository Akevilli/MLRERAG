import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from .base import Base


if TYPE_CHECKING:
    from .document import Document

class Chunk(Base):
    __tablename__ = 'chunks'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False
    )
    document_id: Mapped[str] = mapped_column(ForeignKey('documents.id'))
    document: Mapped["Document"] = relationship(back_populates="chunks", init=False)
    text: Mapped[str] = mapped_column(nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(384), nullable=False)

    __table_args__ = (
        Index(
            'hnsw_chunk_embedding_idx',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={
                'M': 16,
                'ef_construction': 128
            },
            postgresql_ops={
                'embedding': 'vector_cosine_ops'
            }
        ),
    )
