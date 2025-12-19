import uuid

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from .base import Base


class Chunk(Base):
    __tablename__ = 'chunks'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False
    )
    text: Mapped[str] = mapped_column(nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(384), nullable=False)
    chunk_metadata: Mapped[JSONB] = mapped_column(JSONB, nullable=False)

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
