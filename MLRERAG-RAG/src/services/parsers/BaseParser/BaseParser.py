from abc import ABC, abstractmethod

from src.shared.schemas import DocumentMetadata, Document


class Parser(ABC):
    @abstractmethod
    def parse(self, papers: list[DocumentMetadata]) -> list[Document]:
        pass