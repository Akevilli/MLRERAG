import asyncio
from typing import List
from uuid import uuid4

from qdrant_client import AsyncQdrantClient, models

from .schemas import ChunkWithEmbedding


class QdrantRepository:
    """Repository for managing vector storage operations in Qdrant.

    This class provides an interface for uploading text chunks with embeddings
    to a Qdrant collection and performing vector similarity searches with
    tag-based filtering.

    Attributes:
        _client: The async Qdrant client instance for database operations.
        _collection_name: The name of the Qdrant collection to operate on.
    """

    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        """Initializes the QdrantRepository with a client and collection name.

        Args:
            client: An async Qdrant client instance for database operations.
            collection_name: The name of the Qdrant collection to use.
        """
        self._client = client
        self._collection_name = collection_name

    async def upload_chunks(self, chunks: List[ChunkWithEmbedding]) -> List[str]:
        """Uploads text chunks with embeddings to the Qdrant collection.

        Args:
            chunks: List of ChunkWithEmbedding objects containing the text content,
                embedding vector, and associated metadata.

        Returns:
            List of unique string IDs assigned to the uploaded chunks.
        """
        ids = [str(uuid4()) for _ in chunks]

        points = [
            models.PointStruct(
                id=id,
                vector=list(chunk.embedding),
                payload={
                    "text": chunk.content,
                    **chunk.metadata.model_dump(exclude={"tags"}),
                    "tags": [str(tag) for tag in chunk.metadata.tags]
                }
            )
            for id, chunk in zip(ids, chunks)
        ]

        await asyncio.to_thread(lambda: self._client.upload_points(self._collection_name, points=points))

        return ids

    async def query(self, queries: List[List[float]], tags: List[str]) -> models.QueryResponse:
        """Performs a vector similarity search with tag-based filtering.

        Uses Reciprocal Rank Fusion (RRF) to combine results from multiple
        query vectors.

        Args:
            queries: List of embedding vectors to search for.
            tags: List of tags to filter results. Results must match at least
                one of the provided tags.

        Returns:
            QueryResponse containing the most relevant points with payloads.
        """
        tags_filter = [
            models.FieldCondition(
                key="tags",
                match=models.MatchPhrase(phrase=tag)
            )
            for tag in tags
        ]
        should_filter = models.Filter(
            should=tags_filter,
        )
        prefetch = [
            models.Prefetch(
                query=query,
                filter=should_filter,
                limit=20
            )
            for query in queries
        ]

        results = await self._client.query_points(
            collection_name=self._collection_name,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            with_payload=True,
            limit=5
        )

        return results