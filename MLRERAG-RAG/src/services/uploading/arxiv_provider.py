from typing import List

import arxiv

from src.shared.schemas import Metadata


class ArxivProvider:
    def __init__(self):
        self.__arxiv_client = arxiv.Client()

    def download(self, id_list: list[str]) -> List[Metadata]:
        papers = self.__arxiv_client.results(arxiv.Search(id_list=id_list))

        metadata = []

        for paper in papers:
            metadata.append(
                Metadata(
                    paper_id=paper.get_short_id(),
                    title=paper.title,
                    summary=paper.summary,
                    published_at=paper.published.isoformat(),
                    source_url=paper.pdf_url,
                    authors=[author.name for author in paper.authors],
                )
            )

            paper.download_pdf(dirpath="./papers", filename=f"{paper.get_short_id()}.pdf")

        return metadata