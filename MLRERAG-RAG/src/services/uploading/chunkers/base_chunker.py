from abc import ABC, abstractmethod
from typing import List

from src.shared.schemas import ArxivPaperWithTags, Chunk


class Chunker(ABC):
    """Abstract base class for paper chunking strategies.

    Defines the interface for chunking papers into smaller segments
    for downstream processing in the upload pipeline.
    """

    @abstractmethod
    def chunk(self, papers: List[ArxivPaperWithTags]) -> List[Chunk]:
        """Split papers into chunks according to the chunking strategy.

        Args:
            papers: List of papers with tags to be chunked.

        Returns:
            List of chunks derived from the input papers.
        """
        pass