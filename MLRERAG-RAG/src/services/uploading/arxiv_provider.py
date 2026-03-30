import asyncio
from logging import getLogger
from typing import List, AsyncGenerator, Tuple

from httpx import AsyncClient
from arxiv import Client, Search

from src.shared.schemas import ArxivMetadata


class ArxivProvider:
    """Provider for fetching metadata and downloading papers from arXiv."""

    def __init__(self, arxiv_client: Client, httpx_client: AsyncClient):
        self._arxiv_client = arxiv_client
        self._httpx_client = httpx_client

    async def get_metadata(self, id_list: List[str]) -> List[ArxivMetadata]:
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
        query = Search(id_list=id_list)

        def _fetch():
            return list(self._arxiv_client.results(query))

        response = await asyncio.to_thread(_fetch)

        for paper in response:
            paper_response = await self._httpx_client.get(paper.pdf_url, timeout=60)

            if paper_response.status_code == 200:
                yield paper.get_short_id().split("v")[0], paper_response.content

            await asyncio.sleep(1)
