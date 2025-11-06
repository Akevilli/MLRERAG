from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from .base_embedder import Embedder


class HuggingFaceEmbedder(Embedder):
    def __init__(self, embedder: HuggingFaceEmbeddings):
        self.embedder = embedder

    def embed_documents(self, documents: list[dict[str, str | list]]) -> list[dict]:
        documents_with_embeddings = documents

        for doc_index, document in enumerate(documents):
            for chunk_index, chunk in enumerate(document["chunks"]):
                embedding = self.embedder.embed_query(chunk)
                documents_with_embeddings[doc_index]["chunks"][chunk_index] = {
                    "text": chunk,
                    "chunk_index": chunk_index,
                    "embedding": embedding
                }

        return documents_with_embeddings

    def embed_query(self, query: str) -> dict:
        embedding = self.embedder.embed_query(query)

        return {"query": query, "embedding": embedding}