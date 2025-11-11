from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.dependencies import get_session, get_rag_service
from ..schemas import UploadSchema, UploadResponseSchema, QuerySchema, QueryResponseSchema
from src.services.rag import RAGService

router = APIRouter()


@router.put(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponseSchema
)
def upload(
    upload_data: UploadSchema,
    _rag_service: RAGService = Depends(get_rag_service),
    _session: Session = Depends(get_session)
):
    uploaded_documents = _rag_service.upload(upload_data, session=_session)

    return uploaded_documents


@router.post(
    "/generate_answer",
    status_code=status.HTTP_200_OK,
    response_model=QueryResponseSchema
)
def generate_answer(
    query: QuerySchema,
    _rag_service: RAGService = Depends(get_rag_service),
):
    response = _rag_service.generate_answer(query)
    return response