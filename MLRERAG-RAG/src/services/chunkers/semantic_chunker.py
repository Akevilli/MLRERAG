from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.core import Document
from langchain_experimental.text_splitter import SemanticChunker

from .base_chunker import Chunker



class SemanticBaseChunker(Chunker):
    def __init__(self, model: str, device: str):
        self.model = model
        self.device = device
        self.embedder = HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.chunker = SemanticChunker(self.embedder)

    def chunk(self, documents: list[Document]) -> list[dict]:
        documents_chunks = []

        for document in documents:
            chunks = self.chunker.split_text(document.text)
            documents_chunks.append({
                "document": document.extra_info["file_name"].replace("./papers/", "").replace(".pdf", ""),
                "chunks": chunks,
            })

        return documents_chunks