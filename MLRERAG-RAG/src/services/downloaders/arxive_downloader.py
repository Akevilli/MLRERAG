import arxiv

from .base_downloader import Downloader


class ArxivDownloader(Downloader):
    def download(self, ids: list[str]) -> list[str]:
        papers = arxiv.Client().results(arxiv.Search(id_list=ids))
        paths = []


        for index, paper in enumerate(papers):
            paper.download_pdf(dirpath="./papers", filename=f"{ids[index]}.pdf")
            paths.append(f"./papers/{ids[index]}.pdf")

        return paths