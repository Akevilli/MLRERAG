from sqlalchemy import select
from sqlalchemy.orm import Session

from ..BaseRepository import BaseRepository
from ...models import Chunk


class ChunkRepository(BaseRepository):
    def __init__(self):
        super().__init__(Chunk)


    def semantic_search(self, embedding: list[float], session: Session, limit: int = 50) -> list[Chunk]:
        query = select(Chunk).order_by(Chunk.embedding.cosine_distance(embedding)).limit(limit)

        result = session.execute(query).scalars().all()
        return result
