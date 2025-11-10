from abc import ABC, abstractmethod

from .schemas import ChunkWithEmbedding
from src.services.chunkers import Chunk


class Embedder(ABC):
    @abstractmethod
    def embed_documents(self, documents: list[Chunk]) -> list[ChunkWithEmbedding]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> dict:
        pass