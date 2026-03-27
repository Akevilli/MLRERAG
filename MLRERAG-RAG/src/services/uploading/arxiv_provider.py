import asyncio
from typing import List, AsyncGenerator, Tuple

from httpx import AsyncClient
from arxiv import Client, Search

from src.shared.schemas import ArxivMetadata


class ArxivProvider:
    def __init__(self, arxiv_client: Client, httpx_client: AsyncClient):
        self._arxiv_client = arxiv_client
        self._httpx_client = httpx_client

    async def get_metadata(self, id_list: List[str]) -> List[ArxivMetadata]:
        response = await asyncio.to_thread(lambda: list(self._arxiv_client.results(Search(id_list=id_list))))
        metadata = [
            ArxivMetadata(
                arxiv_id=paper_metadata.get_short_id(),
                title=paper_metadata.title,
                summary=paper_metadata.summary,
                source_url=paper_metadata.source_url(),
                authors=[author.name for author in paper_metadata.authors],
            )
            for paper_metadata in response
        ]

        return metadata

    async def download(self, id_list: List[str]) -> AsyncGenerator[Tuple[str, bytes], None]:
        response = await asyncio.to_thread(lambda: list(self._arxiv_client.results(Search(id_list=id_list))))

        for paper in response:
            paper_response = await self._httpx_client.get(paper.pdf_url, timeout=60)

            if paper_response.status_code == 200:
                yield paper.get_short_id(), paper_response.content

            await asyncio.sleep(1)
