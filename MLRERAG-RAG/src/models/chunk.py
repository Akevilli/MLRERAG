import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    document_id: Mapped[str] = mapped_column(ForeignKey('documents.id'))
    document: Mapped["Document"] = relationship(back_populates="chunks")
    text: Mapped[str] = mapped_column(nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(384), nullable=False)
