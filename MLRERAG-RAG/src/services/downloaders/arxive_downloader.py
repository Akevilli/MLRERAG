import arxiv

from .base_downloader import Downloader
from .schemas import DocumentInfo
from src.api.schemas import UploadSchema


class ArxivDownloader(Downloader):
    def download(self, upload_data: UploadSchema) -> list[DocumentInfo]:
        papers = arxiv.Client().results(arxiv.Search(id_list=upload_data.id_list))
        infos = []

        for index, paper in enumerate(papers):
            document_info = DocumentInfo(
                id=upload_data.id_list[index],
                title=paper.title,
                summary=paper.summary,
                published_at=paper.published,
                source_url=paper.pdf_url
            )
            paper.download_pdf(dirpath="./papers", filename=f"{upload_data.id_list[index]}.pdf")
            infos.append(document_info)

        return infos