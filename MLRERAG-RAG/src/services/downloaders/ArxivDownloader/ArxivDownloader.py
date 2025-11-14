from time import sleep

import arxiv

from src.api.schemas import UploadSchema
from ..BaseDownloader import Downloader
from ..schemas import DocumentInfo


class ArxivDownloader(Downloader):
    def __init__(self):
        self.__arxiv = arxiv.Client()

    def download(self, upload_data: UploadSchema) -> list[DocumentInfo]:
        papers = self.__arxiv.results(arxiv.Search(id_list=upload_data.id_list))
        infos = []
        for index, paper in enumerate(papers):
            document_info = DocumentInfo(
                id=upload_data.id_list[index],
                title=paper.title,
                summary=paper.summary,
                published_at=paper.published,
                source_url=paper.pdf_url,
            )
            paper.download_pdf(dirpath="./papers", filename=f"{upload_data.id_list[index]}.pdf")
            infos.append(document_info)
            sleep(3)

        return infos