from typing import List, Tuple, Optional
from abc import ABC, abstractmethod

from src.shared.schemas import ArxivMetadata, ArxivPaper, FileUploadDTO


class Parser(ABC):
    """Abstract base class for paper parsers.

    Defines the interface for parsing raw PDF content into structured
    ArxivPaper objects with sections, tables, and references.
    """

    @abstractmethod
    async def parse(self, unloaded_papers: List[Tuple[Optional[ArxivMetadata], bytes]]) -> List[ArxivPaper]:
        """Parses raw PDF content into structured paper objects.

        Args:
            unloaded_papers: List of tuples containing paper metadata and raw PDF bytes.

        Returns:
            List of ArxivPaper objects with extracted sections, tables, and references.
        """
        pass

    @abstractmethod
    async def parse_files(self, files_dto: FileUploadDTO) -> List[ArxivPaper]:
        pass