from sqlalchemy.orm import Session

from src.models import Chunk
from src.repositories import ChunkRepository
from src.services.embedders.schemas import ChunkWithEmbedding


class ChunkService:
    def __init__(self, chunk_repository: ChunkRepository):
        self.__chunk_repository = chunk_repository

    def create(self, new_chunks: list[ChunkWithEmbedding], session: Session):
        chunks = [Chunk(**chunk.model_dump()) for chunk in new_chunks]

        self.__chunk_repository.create(chunks, session)


    def retrieval(self, embedding: list[float], session: Session) -> list[Chunk]:
        chunks = self.__chunk_repository.semantic_search(embedding, session, 20)
        return chunks