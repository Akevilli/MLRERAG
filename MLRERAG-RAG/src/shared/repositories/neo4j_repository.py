from typing import List

from neo4j import AsyncSession

from ..schemas import ArxivPaper, ArxivMetadata


class Neo4jRepository:

    def __init__(
            self,
            session: AsyncSession,
    ):
        self._session = session

    async def upload_papers(self, papers: List[ArxivPaper], cited_papers_metadata: List[ArxivMetadata]):
        paper_jsons = [paper.model_dump(mode="json") for paper in papers]
        cited_papers_metadata_jsons = [cited_paper_metadata.model_dump(mode="json") for cited_paper_metadata in cited_papers_metadata]
        await self._session.execute_write(self._create_paper_hierarchy, paper_jsons)
        await self._session.execute_write(self._create_cites_structure, papers=paper_jsons, cited_papers_metadata=cited_papers_metadata_jsons)

    async def _create_paper_hierarchy(self, tx, payload):
        await tx.run("CALL custom.rag.create_paper_hierarchy($papers)", papers=payload)

    async def _create_cites_structure(self, tx, papers, cited_papers_metadata):
        await tx.run("CALL custom.rag.create_cites_links($papers, $cited_papers_metadata)", papers=papers, cited_papers_metadata=cited_papers_metadata)

