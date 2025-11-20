from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from src.services.chunks import Chunk, ChunkWithEmbedding
from ..BaseEmbedder import Embedder


class HuggingFaceEmbedder(Embedder):
    def __init__(self, embedder: HuggingFaceEmbeddings):
        self.embedder = embedder

    def embed_documents(self, chunks: list[Chunk]) -> list[ChunkWithEmbedding]:
        chunks_with_embeddings: list[ChunkWithEmbedding] = []

        for chunk in chunks:
            if str.isspace(chunk.text) or chunk.text == "":
                continue

            chunk_with_embeddings = ChunkWithEmbedding(
                **chunk.model_dump(),
                embedding=self.embedder.embed_query(chunk.text)
            )

            chunks_with_embeddings.append(chunk_with_embeddings)

        return chunks_with_embeddings


    def embed_query(self, query: str) -> list[float]:
        embedding = self.embedder.embed_query(query)

        return embedding