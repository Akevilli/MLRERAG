from langchain_experimental.text_splitter import SemanticChunker

from ..BaseChunker import Chunker
from src.services.chunks import Chunk, ChunkMetadata
from src.services.parsers import Document


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
                        document_id=document.document_id,
                        title=document.title,
                        summary=document.summary,
                        source_url=document.source_url,
                        published_at=document.published_at,
                        authors=document.authors,
                        page=document.page,
                        keywords=document.keywords
                    )
                )
                
                chunks.append(chunk)

        return chunks