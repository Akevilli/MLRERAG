from abc import ABC, abstractmethod

from src.services.parsers import Document
from .schema import Chunk


class Chunker(ABC):
    @abstractmethod
    def chunk(self, documents: list[Document]) -> list[Chunk]:
        pass