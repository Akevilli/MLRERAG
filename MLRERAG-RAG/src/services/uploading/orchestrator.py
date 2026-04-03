from datetime import datetime

from loguru import logger

from src.shared.schemas import (
    PaperUploadDTO
)
from .providers import Provider
from .parsers import Parser
from .taggers import Tagger
from .chunkers import Chunker
from src.services.uploading.papers import PaperService
from src.shared.embedders import Embedder
from src.shared.lib import get_batch


class PaperIngestionService:
    """Orchestrates the paper ingestion pipeline.

    Coordinates the flow of paper processing from metadata retrieval through
    downloading, parsing, and tagging.

    Attributes:
        _arxiv_provider: Provider for fetching arXiv metadata and downloads.
        _paper_service: Service for managing paper persistence.
        _parser: Parser for extracting structured content from PDFs.
        _tagger: Tagger for assigning semantic tags to papers.
        _batch_size: Number of papers to process in each batch.
    """

    def __init__(
            self,
            arxiv_provider: Provider,
            paper_service: PaperService,
            parser: Parser,
            tagger: Tagger,
            chunker: Chunker,
            embedder: Embedder,
            batch_size: int
    ):
        """Initializes the PaperIngestionService with required dependencies.

        Args:
            arxiv_provider: Provider for fetching arXiv metadata and downloading PDFs.
            paper_service: Service for paper record management.
            parser: Parser for extracting structured data from PDFs.
            tagger: Tagger for generating semantic tags.
            batch_size: Number of papers to process per batch during download.
        """
        self._arxiv_provider = arxiv_provider
        self._paper_service = paper_service
        self._parser = parser
        self._tagger = tagger
        self._chunker = chunker
        self._embedder = embedder
        self._batch_size = batch_size

    async def process(self, upload_dto: PaperUploadDTO):
        """Processes a list of papers through the complete ingestion pipeline.

        Args:
            upload_dto: DTO containing the list of arXiv IDs to process.

        Returns:
            List of ArxivPaperWithTags containing processed papers with tags.
        """
        result = []
        logger.debug(f"Processing paper(s) {upload_dto.id_list}.")
        arxiv_metadata = await self._arxiv_provider.get_metadata(upload_dto.id_list)
        unloaded_arxiv_metadata = await self._paper_service.register_papers(arxiv_metadata)
        download_generator = self._arxiv_provider.download([paper.arxiv_id for paper in unloaded_arxiv_metadata])
        arxiv_metadata_map = {metadata.arxiv_id: metadata for metadata in unloaded_arxiv_metadata}

        await self._paper_service.delete_papers(upload_dto.id_list) # delete

        logger.debug(f"Start downloading paper(s) {[metadata.arxiv_id for metadata in unloaded_arxiv_metadata]}.")
        async for batch in get_batch(download_generator, self._batch_size):
            if not batch:
                continue

            current_batch = []

            for paper_id, paper_bytes in batch:
                current_batch.append((arxiv_metadata_map[paper_id], paper_bytes))

            parsing_start = datetime.now()
            arxiv_papers = await self._parser.parse(current_batch)
            parsing_end = datetime.now()
            logger.debug(
                f"Paper(s) {[arxiv_paper.metadata.arxiv_id for arxiv_paper in arxiv_papers]} wa(s/re) parsed. "
                f"Total time: {(parsing_end - parsing_start).total_seconds()} seconds."
            )

            tagging_start = datetime.now()
            tagged_arxiv_papers = await self._tagger.tag(arxiv_papers)
            tagging_end = datetime.now()
            logger.debug(
                f"Paper(s) {[arxiv_paper.metadata.arxiv_id for arxiv_paper in tagged_arxiv_papers]} wa(s/re) tagged. "
                f"Total time: {(tagging_end - tagging_start).total_seconds()} seconds. "
            )

            chunks = self._chunker.chunk(tagged_arxiv_papers)
            logger.debug(
                f"Paper(s) {[arxiv_paper.metadata.arxiv_id for arxiv_paper in tagged_arxiv_papers]} wa(s/re) chunked. "
                f"Total chunks: {len(chunks)}."
            )

            embedding_start = datetime.now()
            chunks_with_embeddings = await self._embedder.embed_document(chunks)
            embedding_end = datetime.now()
            logger.debug(
                f"{len(chunks_with_embeddings)} chunks were embedded."
                f"Total time: {(embedding_end - embedding_start).total_seconds()} seconds."
            )

            result.extend(chunks_with_embeddings)

        return result
