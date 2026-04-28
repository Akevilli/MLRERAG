from typing import List, Dict, Type, TypeVar

from loguru import logger
from neo4j.graph import Node, Relationship

from src.shared.repositories import QdrantRepository, Neo4jRepository
from src.shared.schemas import Table
from .schemas import RetrievedDocumentMetadata, RetrievedChunk, RetrievedChunkedSection, RetrievedDocument

T = TypeVar('T')


class SearchEngine:
    def __init__(
            self,
            qdrant_repository: QdrantRepository,
            neo4j_repository: Neo4jRepository,
    ):
        self._qdrant_repository = qdrant_repository
        self._neo4j_repository = neo4j_repository

    async def search(self, queries: List[List[float]], tags: List[str]) -> List[RetrievedDocument]:
        seeds = await self._qdrant_repository.query(queries, tags)
        ids = [seed.id for seed in seeds]
        logger.info(f"Seeds: {ids}")

        response = (await self._neo4j_repository.extend_seeds(ids))[0]["response"]
        papers = []

        for paper in response:
            paper_metadata = RetrievedDocumentMetadata(**paper)
            sections = [RetrievedChunkedSection.model_validate(section) for section in paper["sections"]]
            tables = []
            cited_papers = []

            for section in sections:
                for chunk in section.chunks:
                    tables.extend(chunk.tables)
                    cited_papers.extend(chunk.references)

            papers.append(
                RetrievedDocument(
                    metadata=paper_metadata,
                    sections=sections,
                    tables=tables,
                    references=cited_papers,
                )
            )

        return papers

    def _get_tables(self, nodes: List[Node]) -> Dict[str, Table]:
        return self._get_nodes(nodes, Table, "Table")

    def _get_papers_metadata(self, nodes: List[Node]) -> Dict[str, RetrievedDocumentMetadata]:
        return self._get_nodes(nodes, RetrievedDocumentMetadata, "Paper")

    def _get_chunks(
            self,
            nodes: List[Node],
            relationships: List[Relationship],
            references: Dict[str, RetrievedDocumentMetadata],
            tables: Dict[str, Table]
    ) -> Dict[str, RetrievedChunk]:
        result = self._get_nodes(nodes, RetrievedChunk, "Chunk")

        for relationship in relationships:
            if relationship.type == "HAS_TABLE":
                table = tables[relationship.end_node["id"]]
                result[relationship.start_node["id"]].tables.append(table)
            elif relationship.type == "CITES":
                paper_metadata = references[relationship.end_node["arxiv_id"]]
                result[relationship.start_node["id"]].references.append(paper_metadata)

        return result

    def _get_sections(
            self,
            nodes: List[Node],
            relationships: List[Relationship],
            chunks: Dict[str, RetrievedChunk]
    ) -> Dict[str, RetrievedChunkedSection]:
        result = self._get_nodes(nodes, RetrievedChunkedSection, "Section")

        for relationship in relationships:
            if relationship.type == "PART_OF":
                chunk = chunks[relationship.start_node["id"]]
                result[relationship.end_node["id"]].chunks.append(chunk)

        for section_id, section in result.items():
            result[section_id].chunks = sorted(section.chunks, key=lambda chunk: chunk.position)

        return result

    def _get_papers(
            self,
            relationships: List[Relationship],
            papers_metadata: Dict[str, RetrievedDocumentMetadata],
            sections: Dict[str, RetrievedChunkedSection],
    ) -> List[RetrievedDocument]:
        papers = {
            paper_id: RetrievedDocument(metadata=paper_metadata)
            for paper_id, paper_metadata in papers_metadata.items()
            if paper_metadata.is_loaded
        }

        for relationship in relationships:
            if relationship.type == "BELONGS_TO":
                section = sections[relationship.start_node["id"]]
                papers[relationship.end_node["arxiv_id"]].sections.append(section)

        for paper in papers.values():
            table_ids = set()
            reference_ids = set()

            for section in paper.sections:
                for chunk in section.chunks:
                    for table in chunk.tables:
                        if table.id not in table_ids:
                            table_ids.add(table.id)
                            paper.tables.append(table)
                    for reference in chunk.references:
                        if reference.arxiv_id not in reference_ids:
                            reference_ids.add(reference.arxiv_id)
                            paper.references.append(reference)


        return list(papers.values())


    def _get_nodes[T](self, nodes: List[Node], model: Type[T], label: str) -> Dict[str, T]:
        return {node["id"] or node["arxiv_id"]: model(**node._properties) for node in nodes if label in node.labels}