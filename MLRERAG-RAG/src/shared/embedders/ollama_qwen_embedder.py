import asyncio
from typing import List, Sequence

from ollama import AsyncClient
from loguru import logger

from .base_embedder import Embedder
from ..schemas import Chunk, ChunkWithEmbedding
from ..lib import get_batch


class OllamQwenEmbedder(Embedder):
    """Embedder implementation using Ollama with Qwen models.

    Provides document and query embeddings via an Ollama async client,
    with configurable batch processing and concurrency limiting.

    Attributes:
        _ollama_client: Async Ollama client for making embedding requests.
        _model: Name of the Ollama model to use for embeddings.
        _batch_size: Number of texts to process in each batch request.
        _embedding_dim: Dimensionality of the output embedding vectors.
        _semaphore: Semaphore for limiting concurrent requests.
    """

    def __init__(
            self,
            ollama_client: AsyncClient,
            model: str,
            batch_size: int,
            embedding_dim: int
    ):
        """Initialize the Ollama Qwen embedder.

        Args:
            ollama_client: Async Ollama client instance for API communication.
            model: Name of the embedding model to use (e.g., 'nomic-embed-text').
            batch_size: Maximum number of texts to include in a single API request.
            embedding_dim: Target dimensionality for output embeddings.
        """
        self._ollama_client = ollama_client
        self._model = model
        self._batch_size = batch_size
        self._embedding_dim=embedding_dim

        self._semaphore = asyncio.Semaphore(3)

    async def embed_document(self, chunks: List[Chunk]) -> List[ChunkWithEmbedding]:
        """Embed document chunks with retrieval-optimized prompts.

        Processes chunks in batches, prepending document-specific instructions
        to optimize embeddings for document retrieval use cases.

        Args:
            chunks: List of Chunk objects containing document content to embed.

        Returns:
            List of ChunkWithEmbedding objects with original chunk data and
            corresponding embedding vectors.
        """
        request_texts = self._add_request([chunk.content for chunk in chunks], True)
        logger.info(f"Request texts: {request_texts}")
        all_embeddings = []

        async with self._semaphore:
            async for batch in get_batch(request_texts, self._batch_size):
                response = await self._ollama_client.embed(
                    model=self._model,
                    input=batch,
                    dimensions=self._embedding_dim,
                )
                all_embeddings.extend(response.embeddings)

        result = [
            ChunkWithEmbedding(
                **chunk.model_dump(),
                embedding=embedding)
            for chunk, embedding in zip(chunks, all_embeddings)
        ]

        return result

    async def embed_query(self, query: List[str]) -> Sequence[Sequence[float]]:
        """Embed search queries with query-optimized prompts.

        Prepends query-specific instructions to optimize embeddings for
        semantic search and passage retrieval.

        Args:
            query: List of query strings to embed.

        Returns:
            Sequence of embedding vectors for the input queries.
        """
        query = self._add_request(query)

        async with self._semaphore:
            response = await self._ollama_client.embed(
                model=self._model,
                input=query,
                dimensions=self._embedding_dim,
            )

        return response.embeddings

    def _add_request(self, texts: List[str], is_document: bool = False) -> List[str]:
        """Prepend instruction prompts to texts for embedding optimization.

        Adds task-specific prompts that guide the embedding model to produce
        vectors optimized for either document indexing or query matching.

        Args:
            texts: List of raw text strings to prepare.
            is_document: If True, use document retrieval prompt; otherwise use
                query retrieval prompt.

        Returns:
            List of texts with prepended instruction prompts.
        """
        if is_document:
            prompt = "Instruct: Represent this document for retrieval\nQuery: "
        else:
            prompt = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "

        return [f"{prompt}{text}" for text in texts]

