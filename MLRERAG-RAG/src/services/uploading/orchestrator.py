from src.shared.schemas import (
    PaperUploadDTO
)
from .arxiv_provider import ArxivProvider
from .parsers import Parser
from src.services.uploading.papers import PaperService


class PaperIngestionService:
    def __init__(
            self,
            arxiv_provider: ArxivProvider,
            paper_service: PaperService,
            parser: Parser,
    ):
        self._arxiv_provider = arxiv_provider
        self._paper_service = paper_service
        self._parser = parser

    async def process(self, upload_dto: PaperUploadDTO):
        try:
            result = []
            arxiv_metadata = await self._arxiv_provider.get_metadata(upload_dto.id_list)
            unloaded_arxiv_metadata = await self._paper_service.register_papers(arxiv_metadata)
            download_generator = self._arxiv_provider.download([paper.arxiv_id for paper in unloaded_arxiv_metadata])
            arxiv_metadata_map = {metadata.arxiv_id: metadata for metadata in unloaded_arxiv_metadata}

            await self._paper_service.delete_papers([metadata.arxiv_id for metadata in unloaded_arxiv_metadata]) # delete

            async for paper_id, paper_bytes in download_generator:
                paper_metadata = arxiv_metadata_map[paper_id]
                parser_output = await self._parser.parse([(paper_metadata, paper_bytes)])
                result.append(parser_output)

            return result
        except:
            await self._paper_service.delete_papers(upload_dto.id_list)