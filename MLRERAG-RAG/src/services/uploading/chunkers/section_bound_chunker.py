from typing import List

from src.shared.schemas import ArxivPaperWithTags
from .schemas import Chunk, ChunkMetadata
from .base_chunker import Chunker


class SectionBoundChunker(Chunker):
    """Chunker that respects section boundaries when splitting papers.

    This chunker splits papers into chunks while preserving section boundaries.
    It processes each section separately and splits content based on a
    configurable chunk size with overlap for context preservation.

    Attributes:
        _chunk_size: Target size for each chunk in characters.
        _overlap: Number of characters to overlap between adjacent chunks.
    """

    def __init__(self, chunk_size: int, overlap: int):
        """Initialize the section-bound chunker.

        Args:
            chunk_size: Target size for each chunk in characters.
            overlap: Overlap size between adjacent chunks in characters.
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, papers: List[ArxivPaperWithTags]) -> List[Chunk]:
        """Split papers into chunks respecting section boundaries.

        Processes each paper's sections separately, splitting paragraphs
        into chunks of the configured size while maintaining overlap
        between adjacent chunks for context preservation.

        Args:
            papers: List of papers with tags to be chunked. Each paper
                contains sections with paragraphs that will be processed.

        Returns:
            List of Chunk objects with content and metadata including
            source paper information, tags, page number, and section name.
        """
        result = []

        for paper in papers:
            paper_metadata = paper.metadata.model_dump()

            for section in paper.sections:
                new_chunk_content = ""
                current_page = section.page

                for paragraph in section.paragraphs:
                    if new_chunk_content:
                        new_chunk_content += " " + paragraph.text
                    else:
                        new_chunk_content = paragraph.text
                        current_page = paragraph.page

                    while len(new_chunk_content) >= self._chunk_size:
                        split_idx = new_chunk_content.find(" ", self._chunk_size)


                        if split_idx < 0 or split_idx > self._chunk_size + 20:
                            split_idx = new_chunk_content.rfind(" ", 0, self._chunk_size)

                        if split_idx <= self._overlap:
                            split_idx = self._chunk_size

                        result.append(Chunk(
                            content=new_chunk_content[:split_idx].strip(),
                            metadata=ChunkMetadata(
                                **paper_metadata,
                                tags=paper.tags,
                                page=current_page,
                                section_name=section.title
                            )
                        ))

                        start_index = new_chunk_content.find(" ", split_idx - self._overlap, split_idx)
                        if start_index < 0:
                            start_index = split_idx - self._overlap

                        new_chunk_content = new_chunk_content[start_index:].strip()

                if new_chunk_content:
                    result.append(Chunk(
                        content=new_chunk_content,
                        metadata=ChunkMetadata(
                            **paper_metadata,
                            tags=paper.tags,
                            page=current_page,
                            section_name=section.title
                        )
                    ))

        return result
