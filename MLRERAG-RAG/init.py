import asyncio
import sys
import selectors
from pathlib import Path

from qdrant_client import models

from src.shared.database import Base, engine, qdrant_client, neo4j_client
from src.core.config import settings


async def init():
    # Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Qdrant
    await qdrant_client.delete_collection(collection_name=settings.VECTOR_DB_COLLECTION)
    await qdrant_client.create_collection(
        collection_name=settings.VECTOR_DB_COLLECTION,
        vectors_config=models.VectorParams(
            size=settings.EMBEDDING_DIM,
            distance=models.Distance.COSINE,
            on_disk=True
        ),
        hnsw_config=models.HnswConfigDiff(
            on_disk=True,
            m=16,
            ef_construct=160,
        )
    )

    await qdrant_client.create_payload_index(
        collection_name=settings.VECTOR_DB_COLLECTION,
        field_name="tags",
        field_schema=models.TextIndexParams(
            on_disk=True,
            type=models.TextIndexType.TEXT,
            tokenizer=models.TokenizerType.WORD,
            lowercase=True,
            phrase_matching=True,
        ),
    )

    # Neo4j
    drop_all_command = Path(f"{settings.BASE_DIR}/.init/neo4j/procedures/01_drop_old_procedures.cypher").read_text()
    async with neo4j_client.session(database="system") as session:
        await session.execute_write(lambda tx: tx.run(drop_all_command))

    create_paper_hierarchy_procedure = Path(f"{settings.BASE_DIR}/.init/neo4j/procedures/02_create_paper_hierarchy.cypher").read_text()
    create_cites_links_procedure = Path(f"{settings.BASE_DIR}/.init/neo4j/procedures/03_create_cites_links.cypher").read_text()
    extend_seeds_procedure = Path(f"{settings.BASE_DIR}/.init/neo4j/procedures/04_extend_seeds.cypher").read_text()
    async with neo4j_client.session(database=settings.GRAPH_DB_DATABASE) as session:
        await session.execute_write(lambda tx: tx.run(create_paper_hierarchy_procedure))
        await session.execute_write(lambda tx: tx.run(create_cites_links_procedure))
        await session.execute_write(lambda tx: tx.run(extend_seeds_procedure))


if __name__ == "__main__":
    if sys.platform == 'win32':
        loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.run(init(), loop_factory=loop_factory)
    else:
        asyncio.run(init())