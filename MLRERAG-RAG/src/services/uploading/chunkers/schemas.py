from typing import List

from pydantic import BaseModel, Field

from src.shared.schemas import ArxivMetadata, PaperTag


class ChunkMetadata(ArxivMetadata):
    """Metadata associated with a paper chunk.

    Extends ArxivMetadata with chunk-specific information including
    tags, page location, and section name.

    Attributes:
        tags: List of paper tags associated with the chunk.
        page: Page number where the chunk starts.
        section_name: Name of the section containing the chunk.
    """

    tags: List[PaperTag] = Field(description="List of paper tags.")
    page: str = Field(description="Page where chunk starts.")
    section_name: str = Field(description="Section where chunk locates.")

class Chunk(BaseModel):
    """Schema representing a paper chunk for the uploading process.

    A chunk is a segment of a paper's content with associated metadata,
    used for downstream processing and storage.

    Attributes:
        content: The text content of the chunk.
        metadata: Metadata describing the chunk's source and location.
    """

    content: str = Field(description="Chunk content.")
    metadata: ChunkMetadata = Field(description="Chunk metadata.")