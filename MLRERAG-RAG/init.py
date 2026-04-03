import asyncio
import sys
import selectors

from qdrant_client import models

from src.shared.database import Base, engine, qdrant_client
from src.core.config import settings


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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


if __name__ == "__main__":
    if sys.platform == 'win32':
        loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.run(init(), loop_factory=loop_factory)
    else:
        asyncio.run(init())