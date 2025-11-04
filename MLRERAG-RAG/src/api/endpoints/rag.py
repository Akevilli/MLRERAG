from fastapi import APIRouter, Depends

from src.services.downloaders import ArxivDownloader
from src.services.parsers import LlamaParser
from src.services.chunkers import SemanticBaseChunker
from src.dependencies import get_arxiv_downloader, get_llama_parser, get_semantic_chunker
from ..schemas import UploadSchema


router = APIRouter()


@router.put("/upload")
def upload(
    upload_data: UploadSchema,
    arxiv_downloader: ArxivDownloader = Depends(get_arxiv_downloader),
    llama_parser: LlamaParser = Depends(get_llama_parser),
    semantic_chunker: SemanticBaseChunker = Depends(get_semantic_chunker),
):
    paths = arxiv_downloader.download(upload_data.id_list)
    documents = llama_parser.parse(paths)
    results = semantic_chunker.chunk(documents)

    return results