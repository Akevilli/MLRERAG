from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

from .base_chunker import Chunker
from .schema import Chunk
from src.services.parsers import Document



class SemanticBaseChunker(Chunker):
    def __init__(self, embedder: HuggingFaceEmbeddings):
        self.embedder = embedder

        self.chunker = SemanticChunker(
            self.embedder,
            breakpoint_threshold_amount=87.5,
            sentence_split_regex=r"\n{2,}|#{1,3}\s|(?<![|\s*-*])---(?![-*\s*|])|(?<![|\s*])\n(?![\s*|])|(?<![.])\.(?![\d.])|[?!]",
            min_chunk_size=150
        )

    def chunk(self, documents: list[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for document in documents:
            chunks_text = self.chunker.split_text(document.text)

            for index, chunk_text in enumerate(chunks_text):
                chunk = Chunk(
                    document_id=document.id,
                    text=chunk_text,
                    chunk_index=index,
                )
                
                chunks.append(chunk)

        return chunks