from typing import List

from neo4j import AsyncSession

from ..schemas import EmbeddedArxivPaper


class Neo4jRepository:
    _first_layer_query = """
            UNWIND $papers AS paper
            MERGE (p:Paper {arxiv_id: paper.metadata.arxiv_id})
            SET p += paper.metadata,
                p.tags = paper.tags
            
            WITH paper, p
            UNWIND paper.sections AS section
            MERGE (s:Section {id: section.id})
            SET s.number = section.number,
                s.title = section.title,
                s.page = section.page
            MERGE (s)-[:BELONGS_TO]->(p)
            
            WITH section, s
            UNWIND section.chunks AS chunk
            MERGE (c:Chunk {id: chunk.id})
            SET c.text = chunk.text,
                c.page = chunk.page
            MERGE (c)-[:PART_OF]->(s)
            
            WITH section, s, chunk, c
            UNWIND chunk.tables AS table
            MERGE (t:Table {id: table.id})
            ON CREATE SET 
                t.caption = table.caption,
                t.text = table.text,
                t.description = table.description,
                t.page = table.page
            MERGE (c)-[:HAS_TABLE]->(t)
            
            WITH section, s
            UNWIND range(0, size(section.chunks) - 2) AS idx
            MATCH (c1:Chunk {id: section.chunks[idx].id})
            MATCH (c2:Chunk {id: section.chunks[idx + 1].id})
            MERGE (c1)-[:NEXT]->(c2)
            """

    def __init__(
            self,
            session: AsyncSession,
    ):
        self._session = session

    async def upload_papers(self, embedded_papers: List[EmbeddedArxivPaper]):
        paper_jsons = [paper.model_dump(mode="json") for paper in embedded_papers]
        await self._session.execute_write(self._create_tree_structure, paper_jsons)

    async def _create_tree_structure(self, tx, payload):
        await tx.run(self._first_layer_query, papers=payload)

