import asyncio
from typing import List, AsyncGenerator, Tuple

from httpx import AsyncClient
from arxiv import Client, Search

from .base_provider import Provider
from src.shared.schemas import ArxivMetadata


class ArxivProvider(Provider):
    """Provider for fetching metadata and downloading papers from arXiv.

    Uses the official arxiv.py library for metadata retrieval and httpx
    for asynchronous PDF downloads.

    Attributes:
        _arxiv_client: The arxiv.py client for metadata queries.
        _httpx_client: Async HTTP client for downloading PDFs.
    """

    def __init__(self, arxiv_client: Client, httpx_client: AsyncClient):
        """Initializes the ArxivProvider with required clients.

        Args:
            arxiv_client: An arxiv.py Client instance for querying metadata.
            httpx_client: An async HTTP client for downloading PDFs.
        """
        self._arxiv_client = arxiv_client
        self._httpx_client = httpx_client

    async def get_metadata(self, id_list: List[str]) -> List[ArxivMetadata]:
        """Fetches metadata for the specified arXiv IDs.

        Args:
            id_list: List of arXiv IDs (with or without version suffix).

        Returns:
            List of ArxivMetadata objects containing title, summary, authors, etc.
        """
        query = Search(id_list=id_list)

        def _fetch():
            return list(self._arxiv_client.results(query))

        def _get_id_and_version(arxiv_id: str) -> Tuple[str, str]:
            arxiv_id, version = arxiv_id.split("v")
            return arxiv_id, version if version else "1"

        response = await asyncio.to_thread(_fetch)

        metadata = [
            ArxivMetadata(
                arxiv_id=_get_id_and_version(paper_metadata.get_short_id())[0],
                version=_get_id_and_version(paper_metadata.get_short_id())[1],
                title=paper_metadata.title,
                summary=paper_metadata.summary,
                source_url=paper_metadata.pdf_url,
                authors=[author.name for author in paper_metadata.authors],
            )
            for paper_metadata in response
        ]

        return metadata

    async def download(self, id_list: List[str]) -> AsyncGenerator[Tuple[str, bytes], None]:
        """Downloads PDFs for the specified arXiv IDs.

        Args:
            id_list: List of arXiv IDs to download.

        Yields:
            Tuples of (arxiv_id, pdf_bytes) for each successfully downloaded paper.
        """
        query = Search(id_list=id_list)

        def _fetch():
            return list(self._arxiv_client.results(query))

        response = await asyncio.to_thread(_fetch)

        for paper in response:
            paper_response = await self._httpx_client.get(paper.pdf_url, timeout=60)

            if paper_response.status_code == 200:
                yield paper.get_short_id().split("v")[0], paper_response.content

            await asyncio.sleep(3)
