from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core import get_user_payload
from src.services import ChatService, ChatViewDTO
from src.dependencies import get_chat_service
from src.api.schemas import BasePaginationRequestSchema
from src.shared.schemas import PaginationResponseDTO


router = APIRouter()


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=PaginationResponseDTO
)
async def get_my_chats(
    pagination_request: Annotated[BasePaginationRequestSchema, Depends()],
    chat_service: ChatService = Depends(get_chat_service),
    user_credentials: dict = Depends(get_user_payload),
):
    chats = await chat_service.get_chats(pagination_request.to_dto(), user_credentials)
    return chats


@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatViewDTO
)
async def get_chat_by_id(
    chat_id: UUID,
    chat_service: ChatService = Depends(get_chat_service),
    user_credentials: dict = Depends(get_user_payload),
):
    chat = await chat_service.get_by_id(chat_id, user_credentials)
    return chat