from abc import ABC, abstractmethod

from src.shared.schemas import Document, Chunk


class Chunker(ABC):
    @abstractmethod
    def chunk(self, documents: list[Document]) -> list[Chunk]:
        pass