from datetime import datetime

from fastapi import APIRouter, Depends, status

from src.dependencies import get_uploading_orchestrator, get_retrieving_orchestrator
from ..schemas import (
    PaperUploadRequest,
    PaperUploadResponse,
    GenerateAnswerRequest,
    GenerateAnswerResponse
)
from src.services.uploading import PaperIngestionService
from src.services.retrieving import RetrievingService

router = APIRouter()


@router.put(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=PaperUploadResponse
)
async def upload(
    upload_data: PaperUploadRequest,
    _rag_service: PaperIngestionService = Depends(get_uploading_orchestrator),
):
    response = await _rag_service.process(upload_data.to_dto())

    return response


@router.post(
    "/generate_answer",
    status_code=status.HTTP_200_OK,
    response_model=GenerateAnswerResponse
)
async def generate_answer(
    query: GenerateAnswerRequest,
    _rag_service: RetrievingService = Depends(get_retrieving_orchestrator),
):
    response = await _rag_service.generate_answer(query.to_dto())
    return response