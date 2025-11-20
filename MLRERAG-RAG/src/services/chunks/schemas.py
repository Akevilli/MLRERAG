from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    summary: str
    source_url: str
    published_at: str
    authors: list[str]


class ChunkMetadata(DocumentMetadata):
    page: int
    keywords: list[str]


class Chunk(BaseModel):
    text: str
    chunk_metadata: ChunkMetadata


class ChunkWithEmbedding(Chunk):
    embedding: list[float]