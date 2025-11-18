from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core import get_user_payload
from src.services import ChatService, ChatPaginationSchema, ChatSchema
from src.dependencies import get_chat_service, get_session


router = APIRouter()


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ChatPaginationSchema
)
def get_my_chats(
    page: int,
    chat_service: ChatService = Depends(get_chat_service),
    user_credentials: dict = Depends(get_user_payload),
    session: Session = Depends(get_session)
):
    chats = chat_service.get_chats(page, user_credentials, session)
    return chats


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ChatSchema
)
def get_chat_by_id(
    id: UUID,
    chat_service: ChatService = Depends(get_chat_service),
    user_credentials: dict = Depends(get_user_payload),
    session: Session = Depends(get_session)
):
    chat = chat_service.get_by_id(id, user_credentials, session)
    return chat