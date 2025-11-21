from abc import ABC, abstractmethod

from src.services.parsers.schemas import Document
from src.services.chunks import DocumentMetadata


class Parser(ABC):
    @abstractmethod
    def parse(self, papers: list[DocumentMetadata]) -> list[Document]:
        pass