from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def embed_documents(self, documents: list[dict]) -> list[dict]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> dict:
        pass