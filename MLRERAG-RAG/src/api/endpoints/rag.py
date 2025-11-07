from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.services.downloaders import Downloader
from src.services.parsers import Parser
from src.services.chunkers import Chunker
from src.services.embedders import Embedder
from src.services.documents import DocumentService
from src.dependencies import (
    get_arxiv_downloader,
    get_llama_parser,
    get_semantic_chunker,
    get_huggingface_embedder,
    get_document_service,
    get_session
)
from ..schemas import UploadSchema, UploadResponse


router = APIRouter()


@router.put(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse
)
def upload(
    upload_data: UploadSchema,
    arxiv_downloader: Downloader = Depends(get_arxiv_downloader),
    llama_parser: Parser = Depends(get_llama_parser),
    semantic_chunker: Chunker = Depends(get_semantic_chunker),
    embedder: Embedder = Depends(get_huggingface_embedder),
    document_service: DocumentService = Depends(get_document_service),
    session: Session = Depends(get_session)
):
    corrected_upload_data = UploadSchema(
        id_list=document_service.get_unstored_documents(upload_data.id_list, session)
    )

    if len(corrected_upload_data.id_list) == 0:
        return {"saved_documents": corrected_upload_data.id_list}

    documents_info = arxiv_downloader.download(corrected_upload_data)
    documents = llama_parser.parse(documents_info)
    document_service.create(documents, session)
    chunks = semantic_chunker.chunk(documents)
    embedder.embed_documents(chunks)

    return {"saved_documents": corrected_upload_data.id_list}