from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core import get_user_payload
from src.services import RAGService
from ..schemas import RAGQuerySchema
from src.dependencies import get_rag_service, get_session

router = APIRouter()

@router.put(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def process_query(
    query: RAGQuerySchema,
    rag_service: RAGService = Depends(get_rag_service),
    user_credentials: dict = Depends(get_user_payload),
    session: Session = Depends(get_session),
):
    response = rag_service.generate_answer(query, user_credentials, session)
    return response