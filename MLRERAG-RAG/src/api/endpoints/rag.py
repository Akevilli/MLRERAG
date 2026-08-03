from typing import List

from fastapi import APIRouter, Depends, status, File, UploadFile

from src.dependencies import get_uploading_orchestrator, get_retrieving_orchestrator
from ..schemas import (
    PDFDTO,
    FileUploadDTO,
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
    rag_service: PaperIngestionService = Depends(get_uploading_orchestrator),
):
    response = await rag_service.process(upload_data.to_dto())

    return response

@router.post(
    "/upload/pdf",
    status_code=status.HTTP_201_CREATED,
    response_model=PaperUploadResponse
)
async def upload_files(
    files: List[UploadFile] = File(...),
    rag_service: PaperIngestionService = Depends(get_uploading_orchestrator)
):
    pdf_dtos = []
    for file in files:
        content = await file.read()
        pdf_dtos.append(PDFDTO(name=file.filename, content=content))
    
    file_upload_dto = FileUploadDTO(files=pdf_dtos)
    response = await rag_service.process_files(file_upload_dto)
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