from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.dependencies import get_user_service
from src.services import UserService, UserViewDTO

router = APIRouter()


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserViewDTO
)
async def get_user_by_username(
        username: str,
        user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_by_username(username)
    return user


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserViewDTO
)
async def get_user_by_id(
        user_id: UUID,
        user_service: UserService = Depends(get_user_service),
    ):
    user = await user_service.get_by_id(user_id)
    return user
