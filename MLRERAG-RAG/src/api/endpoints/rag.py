from fastapi import APIRouter, Depends, status

from src.dependencies import get_uploading_orchestrator
from ..schemas import (
    PaperUploadRequest,
    PaperUploadResponse,
)
from src.services.uploading import PaperIngestionService

router = APIRouter()


@router.put(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=PaperUploadResponse
)
def upload(
    upload_data: PaperUploadRequest,
    _rag_service: PaperIngestionService = Depends(get_uploading_orchestrator),
):
    uploaded_documents = _rag_service.process(upload_data.to_dto())

    return uploaded_documents


# @router.post(
#     "/generate_answer",
#     status_code=status.HTTP_200_OK,
#     response_model=QueryResponseSchema
# )
# def generate_answer(
#     query: QuerySchema,
#     _rag_service: RAGService = Depends(get_rag_service),
# ):
#     response = _rag_service.generate_answer(query)
#     return response