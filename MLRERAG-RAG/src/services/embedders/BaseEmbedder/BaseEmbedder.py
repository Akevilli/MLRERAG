from abc import ABC, abstractmethod

from src.shared.schemas import Chunk, ChunkWithEmbedding


class Embedder(ABC):
    @abstractmethod
    def embed_documents(self, documents: list[Chunk]) -> list[ChunkWithEmbedding]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> dict:
        pass