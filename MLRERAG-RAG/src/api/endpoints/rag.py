from fastapi import APIRouter, Depends

from src.services.downloaders import Downloader
from src.services.parsers import Parser
from src.services.chunkers import Chunker
from src.services.embedders import Embedder
from src.dependencies import (
    get_arxiv_downloader,
    get_llama_parser,
    get_semantic_chunker,
    get_huggingface_embedder
)
from ..schemas import UploadSchema


router = APIRouter()


@router.put("/upload")
def upload(
    upload_data: UploadSchema,
    arxiv_downloader: Downloader = Depends(get_arxiv_downloader),
    llama_parser: Parser = Depends(get_llama_parser),
    semantic_chunker: Chunker = Depends(get_semantic_chunker),
    embedder: Embedder = Depends(get_huggingface_embedder),
):
    paths = arxiv_downloader.download(upload_data.id_list)
    documents = llama_parser.parse(paths)
    chunks = semantic_chunker.chunk(documents)
    embeddings = embedder.embed_documents(chunks)

    return embeddings