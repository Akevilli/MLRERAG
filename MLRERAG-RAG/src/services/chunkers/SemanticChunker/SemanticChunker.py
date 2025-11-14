from langchain_experimental.text_splitter import SemanticChunker

from ..BaseChunker import Chunker
from src.services.chunkers.schema import Chunk
from src.services.parsers import Document



class SemanticBaseChunker(Chunker):
    def __init__(self, chunker: SemanticChunker):
        self.__chunker = chunker

    def chunk(self, documents: list[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for document in documents:
            chunks_text = self.__chunker.split_text(document.text)

            for index, chunk_text in enumerate(chunks_text):
                chunk = Chunk(
                    document_id=document.id,
                    text=chunk_text,
                    chunk_index=index,
                )
                
                chunks.append(chunk)

        return chunks