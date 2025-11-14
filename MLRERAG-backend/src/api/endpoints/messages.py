from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core import get_user_payload
from src.services import MessageService
from src.dependencies import get_session, get_message_service
from ..schemas import MessageSchema


router = APIRouter()


@router.get(
    "/chats/{chat_id}/messages",
    response_model=list[MessageSchema],
    status_code=status.HTTP_200_OK
)
def get_messages(
    chat_id: UUID,
    message_service: MessageService = Depends(get_message_service),
    session: Session = Depends(get_session)
):
    messages = message_service.get_latest_chat_messages(chat_id, session)
    return messages