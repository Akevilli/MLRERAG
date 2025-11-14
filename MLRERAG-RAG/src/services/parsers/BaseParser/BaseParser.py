from abc import ABC, abstractmethod

from src.services.parsers.schemas import Document
from src.services.downloaders import DocumentInfo


class Parser(ABC):
    @abstractmethod
    def parse(self, papers: list[DocumentInfo]) -> list[Document]:
        pass