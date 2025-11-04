from fastapi import APIRouter, Depends

from src.services.downloaders import ArxivDownloader
from src.services.parsers import LlamaParser
from src.dependencies import get_arxiv_downloader, get_llama_parser
from ..schemas import UploadSchema


router = APIRouter()


@router.put("/upload")
def upload(
    upload_data: UploadSchema,
    arxiv_downloader: ArxivDownloader = Depends(get_arxiv_downloader),
    llama_parser: LlamaParser = Depends(get_llama_parser)
):
    paths = arxiv_downloader.download(upload_data.id_list)
    results = llama_parser.parse(paths)

    return results