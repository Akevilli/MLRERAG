from fastapi import APIRouter, Depends, status

from src.core import get_user_payload
from src.services import RAGService, RAGRServiceResponseDTO
from ..schemas import RAGQuerySchema
from src.dependencies import get_rag_service

router = APIRouter()

@router.put(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RAGRServiceResponseDTO,
)
async def process_query(
    query: RAGQuerySchema,
    rag_service: RAGService = Depends(get_rag_service),
    user_credentials: dict = Depends(get_user_payload),
):
    response = await rag_service.generate_answer(query.to_dto(), user_credentials)
    return response