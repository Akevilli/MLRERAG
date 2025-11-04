from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.dependencies import get_user_service, get_session
from src.services import UserService
from src.models import User
from ..schemas import UserViewSchema


router = APIRouter()


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserViewSchema
)
def get_user_by_username(
        username: str,
        user_service: UserService = Depends(get_user_service),
        session: Session = Depends(get_session),
    ):
    user: User = user_service.get_by_username(username, session)
    return user


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserViewSchema
)
def get_user_by_id(
        id: UUID,
        user_service: UserService = Depends(get_user_service),
        session: Session = Depends(get_session),
    ):
    user: User = user_service.get_by_id(id, session)
    return user
