from abc import ABC, abstractmethod
from typing import List, AsyncGenerator, Tuple

from src.shared.schemas import ArxivMetadata


class Provider(ABC):
    """Abstract base class for paper providers.

    Defines the interface for fetching paper metadata and downloading
    paper content from external sources like arXiv.
    """

    @abstractmethod
    async def get_metadata(self, id_list: List[str]) -> List[ArxivMetadata]:
        """Fetches metadata for the specified paper IDs.

        Args:
            id_list: List of paper identifiers to fetch metadata for.

        Returns:
            List of ArxivMetadata objects containing paper information.
        """
        pass

    @abstractmethod
    def download(self, id_list: List[str]) -> AsyncGenerator[Tuple[str, bytes], None]:
        """Downloads paper content for the specified IDs.

        Args:
            id_list: List of paper identifiers to download.

        Yields:
            Tuples of (paper_id, pdf_bytes) for each successfully downloaded paper.
        """
        pass
