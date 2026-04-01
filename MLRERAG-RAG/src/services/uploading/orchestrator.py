from src.shared.schemas import (
    PaperUploadDTO
)
from .providers import Provider
from .parsers import Parser
from .taggers import Tagger
from .chunkers import Chunker
from .lib import get_batch
from src.services.uploading.papers import PaperService


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
        self._batch_size = batch_size

    async def process(self, upload_dto: PaperUploadDTO):
        """Processes a list of papers through the complete ingestion pipeline.

        Args:
            upload_dto: DTO containing the list of arXiv IDs to process.

        Returns:
            List of ArxivPaperWithTags containing processed papers with tags.
        """
        try:
            result = []
            arxiv_metadata = await self._arxiv_provider.get_metadata(upload_dto.id_list)
            unloaded_arxiv_metadata = await self._paper_service.register_papers(arxiv_metadata)
            download_generator = self._arxiv_provider.download([paper.arxiv_id for paper in unloaded_arxiv_metadata])
            arxiv_metadata_map = {metadata.arxiv_id: metadata for metadata in unloaded_arxiv_metadata}

            await self._paper_service.delete_papers([metadata.arxiv_id for metadata in unloaded_arxiv_metadata]) # delete

            async for batch in get_batch(download_generator, self._batch_size):
                current_batch = []

                for paper_id, paper_bytes in batch:
                    current_batch.append((arxiv_metadata_map[paper_id], paper_bytes))

                arxiv_papers = await self._parser.parse(current_batch)
                tagged_arxiv_papers = await self._tagger.tag(arxiv_papers)
                chunks = self._chunker.chunk(tagged_arxiv_papers)

                result.extend(chunks)

            return result
        except:
            await self._paper_service.delete_papers(upload_dto.id_list)