from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core import get_user_payload
from src.services.messages import MessageService, MessagePaginationSchema
from src.dependencies import get_session, get_message_service


router = APIRouter()


@router.get(
    "/chats/{chat_id}",
    response_model=MessagePaginationSchema,
    status_code=status.HTTP_200_OK
)
def get_messages(
    chat_id: UUID,
    message_service: MessageService = Depends(get_message_service),
    user_credentials: dict = Depends(get_user_payload),
    session: Session = Depends(get_session)
):
    messages = message_service.get_latest_chat_messages(chat_id, user_credentials, session)
    return messages