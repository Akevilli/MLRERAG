from logging import Logger

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from src.services import AuthService
from src.dependencies import get_session, get_auth_service, get_logger
from src.api.schemas import (
    CreateUserSchema, 
    ActivateUserSchema,
    LoginUserSchema,
    LoginedUserView
)


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    new_user_data: CreateUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    logger: Logger = Depends(get_logger)
) -> None:
    user = auth_service.register(new_user_data, session)
    logger.info(f"New user created: {user.username}:{user.email}")


@router.post(
    "/activate",
    status_code=status.HTTP_200_OK
)
def activate(
    activate_user_data: ActivateUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    logger: Logger = Depends(get_logger)
) -> None:
    auth_service.activate(activate_user_data, session)
    logger.info(f"Activated user: {activate_user_data.login}")


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginedUserView
)
def login(
    login_user_data: LoginUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
    session: Session = Depends(get_session),
    logger: Logger = Depends(get_logger)
):
    logined_user = auth_service.login(login_user_data, session)
    logger.info(f"Login user: {logined_user.username}:{logined_user.email}")
    return logined_user