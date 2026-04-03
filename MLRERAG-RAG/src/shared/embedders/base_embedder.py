from abc import ABC, abstractmethod
from typing import List, Sequence

from ..schemas import Chunk, ChunkWithEmbedding


class Embedder(ABC):
    """Abstract base class for text embedding implementations.

    Defines the interface for embedding documents and queries into vector
    representations suitable for semantic search and retrieval tasks.
    """

    @abstractmethod
    async def embed_document(self, chunks: List[Chunk]) -> List[ChunkWithEmbedding]:
        """Embed a list of document chunks into vector representations.

        Args:
            chunks: List of Chunk objects containing the text content to embed.

        Returns:
            List of ChunkWithEmbedding objects with the original chunk data
            and their corresponding embedding vectors.
        """
        pass

    @abstractmethod
    async def embed_query(self, query: List[str]) -> Sequence[Sequence[float]]:
        """Embed search queries into vector representations.

        Args:
            query: List of query strings to embed.

        Returns:
            Sequence of embedding vectors, one for each input query.
        """
        pass