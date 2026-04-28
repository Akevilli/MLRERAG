from fastapi import Depends, APIRouter, status
from loguru import logger

from src.services import (
    AuthService,
    LoginUserResponseDTO,
    RefreshJWTResponseDTO
)
from src.dependencies import get_auth_service
from src.api.schemas import (
    CreateUserRequestSchema,
    ActivateUserRequestSchema,
    LoginUserRequestSchema,
    RefreshJWTRequestSchema,
)


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(
    new_user_data: CreateUserRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    user = await auth_service.register(new_user_data.to_dto())
    logger.info(f"New user was created: {user.username}/{user.email}")


@router.post(
    "/activate",
    status_code=status.HTTP_200_OK
)
async def activate(
    activate_user_data: ActivateUserRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.activate(activate_user_data.to_dto())
    logger.info(f"Activated user: {activate_user_data.login}")


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginUserResponseDTO
)
async def login(
    login_user_data: LoginUserRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    logged_in_user = await auth_service.login(login_user_data.to_dto())
    logger.info(f"User logged in: {logged_in_user.username}/{logged_in_user.email}")
    return logged_in_user


@router.post(
    "/refresh",
    status_code=status.HTTP_201_CREATED,
    response_model=RefreshJWTResponseDTO
)
async def refresh(
    update_jwt_schema: RefreshJWTRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    response = await auth_service.refresh_jwt(update_jwt_schema.to_dto())
    logger.info(f"User: {update_jwt_schema.user_id} updated jwt token.")
    return response
