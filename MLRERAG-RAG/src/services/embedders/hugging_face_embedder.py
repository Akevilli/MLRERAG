from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from .base_embedder import Embedder
from .schemas import ChunkWithEmbedding
from src.services.chunkers import Chunk


class HuggingFaceEmbedder(Embedder):
    def __init__(self, embedder: HuggingFaceEmbeddings):
        self.embedder = embedder

    def embed_documents(self, chunks: list[Chunk]) -> list[ChunkWithEmbedding]:
        chunks_with_embeddings: list[ChunkWithEmbedding] = []

        for chunk in chunks:
            chunk_with_embeddings = ChunkWithEmbedding(
                **chunk.model_dump(),
                embedding=self.embedder.embed_query(chunk.text)
            )

            chunks_with_embeddings.append(chunk_with_embeddings)

        return chunks_with_embeddings


    def embed_query(self, query: str) -> dict:
        embedding = self.embedder.embed_query(query)

        return {"query": query, "embedding": embedding}