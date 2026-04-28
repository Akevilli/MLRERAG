from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core import get_user_payload
from src.api.schemas import BasePaginationRequestSchema
from src.services.messages import MessageService
from src.dependencies import get_message_service
from src.shared.schemas import PaginationResponseDTO

router = APIRouter()


@router.get(
    "/",
    response_model=PaginationResponseDTO,
    status_code=status.HTTP_200_OK
)
async def get_messages(
    chat_id: UUID,
    pagination_request: Annotated[BasePaginationRequestSchema, Depends()],
    message_service: MessageService = Depends(get_message_service),
    user_credentials: dict = Depends(get_user_payload),
):
    messages = await message_service.get_chat_messages(chat_id, pagination_request.to_dto(), user_credentials)
    return messages