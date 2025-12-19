from langchain_experimental.text_splitter import SemanticChunker

from ..BaseChunker import Chunker
from src.shared.schemas import Document, ChunkMetadata, Chunk


class SemanticBaseChunker(Chunker):
    def __init__(
        self,
        chunker: SemanticChunker,
    ):
        self.__chunker = chunker

    def chunk(self, documents: list[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for document in documents:
            chunks_text = self.__chunker.split_text(document.text)

            for index, chunk_text in enumerate(chunks_text):
                chunk = Chunk(
                    text=chunk_text,
                    chunk_metadata=ChunkMetadata(
                        **document.document_metadata.model_dump(),
                        page=document.page
                    )
                )
                
                chunks.append(chunk)

        return chunks