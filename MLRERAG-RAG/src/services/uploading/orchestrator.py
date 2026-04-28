from datetime import datetime

from loguru import logger

from src.shared import PaperUploadDTO, UploadedPaperDTO, Embedder, QdrantRepository, get_batch, Neo4jRepository
from .papers import PaperService
from .providers import Provider
from .parsers import Parser
from .taggers import Tagger
from .chunkers import Chunker


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
            qdrant_repository: QdrantRepository,
            neo4j_repository: Neo4jRepository,
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
        self._qdrant_repository = qdrant_repository
        self._neo4j_repository = neo4j_repository
        self._batch_size = batch_size

    async def process(self, upload_dto: PaperUploadDTO) -> UploadedPaperDTO:
        """Processes a list of papers through the complete ingestion pipeline.

        Args:
            upload_dto: DTO containing the list of arXiv IDs to process.

        Returns:
            List of ArxivPaperWithTags containing processed papers with tags.
        """
        total_loaded = set()
        total_failed = set()
        total_cited = set()

        try:
            logger.debug(f"Processing paper(s) {upload_dto.id_list}.")
            arxiv_metadata = await self._arxiv_provider.get_metadata(upload_dto.id_list)
            unloaded_arxiv_metadata = await self._paper_service.register_papers(arxiv_metadata)
            download_generator = self._arxiv_provider.download([paper.arxiv_id for paper in unloaded_arxiv_metadata])
            arxiv_metadata_map = {metadata.arxiv_id: metadata for metadata in unloaded_arxiv_metadata}

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

                chunked_papers = self._chunker.chunk(tagged_arxiv_papers)
                logger.debug(
                    f"Paper(s) {[arxiv_paper.metadata.arxiv_id for arxiv_paper in tagged_arxiv_papers]} wa(s/re) chunked."
                )

                embedding_start = datetime.now()
                embedded_papers = await self._embedder.embed_document(chunked_papers)
                embedding_end = datetime.now()
                logger.debug(
                    f"Total time: {(embedding_end - embedding_start).total_seconds()} seconds."
                )

                cited_papers_metadata = await self._arxiv_provider.get_metadata([reference.arxiv_id for paper in embedded_papers for reference in paper.references])

                await self._qdrant_repository.upload_chunks(embedded_papers)
                await self._neo4j_repository.upload_papers(chunked_papers, cited_papers_metadata)
                await self._paper_service.mark_as_loaded([paper.metadata for paper in embedded_papers])

                loaded = {paper.metadata.arxiv_id for paper in embedded_papers}
                total_loaded.update(loaded)

                failed = set([item[0].arxiv_id for item in current_batch]) - set(loaded)
                total_failed.update(failed)

                cited = {cited_paper.arxiv_id for paper in embedded_papers for cited_paper in paper.references}
                total_cited.update(cited)

            return UploadedPaperDTO(loaded=total_loaded, failed=total_failed, cited=total_cited)
        except:
            raise
        finally:
            total_failed |= set(upload_dto.id_list) - total_loaded
            await self._paper_service.delete_papers(list(total_failed))