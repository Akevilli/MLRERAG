from langchain_huggingface import HuggingFaceEmbeddings
from llama_index.core import Document
from langchain_experimental.text_splitter import SemanticChunker

from .base_chunker import Chunker



class SemanticBaseChunker(Chunker):
    def __init__(self, embedder: HuggingFaceEmbeddings):
        self.embedder = embedder

        self.chunker = SemanticChunker(
            self.embedder,
            breakpoint_threshold_amount=87.5,
            sentence_split_regex=r"\n{2,}|#{1,3}\s|(?<![|\s*-*])---(?![-*\s*|])|(?<![|\s*])\n(?![\s*|])|(?<![.])\.(?![\d.])|[?!]",
            min_chunk_size=150
        )

    def chunk(self, documents: list[Document]) -> list[dict]:
        documents_chunks = []

        for document in documents:
            chunks = self.chunker.split_text(document.text)
            documents_chunks.append({
                "name": document.extra_info["file_name"].replace("./papers/", "").replace(".pdf", ""),
                "chunks": chunks,
            })

        return documents_chunks