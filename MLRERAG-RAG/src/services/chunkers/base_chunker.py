from abc import ABC, abstractmethod

from llama_index.core import Document


class Chunker(ABC):
    @abstractmethod
    def chunk(self, documents):
        pass