from typing import List
from abc import ABC, abstractmethod

from src.shared.schemas import ArxivPaper, TaggedArxivPaper


class Tagger(ABC):
    """Abstract base class for paper taggers.

    Defines the interface for assigning semantic tags to papers
    based on their content and metadata.
    """

    @abstractmethod
    async def tag(self, papers: List[ArxivPaper]) -> List[TaggedArxivPaper]:
        """Assigns tags to the provided papers.

        Args:
            papers: List of ArxivPaper objects to tag.

        Returns:
            List of ArxivPaperWithTags containing the original papers
            with assigned tags.
        """
        pass