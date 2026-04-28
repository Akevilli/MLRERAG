from uuid import UUID

import bcrypt
from fastapi.exceptions import HTTPException

from .schemas import UserCreateDTO, UserUpdateDTO, UserViewDTO
from src.core import retry_strategy
from src.shared.repositories import UserRepository
from src.shared.databases.postgres.models import User


class UserService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    @staticmethod
    def _get_user_view(user: User) -> UserViewDTO:
        return UserViewDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            is_activated=user.is_activated
        )

    @staticmethod
    def _raise_404_if_none(user: User | None) -> None:
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    @retry_strategy
    async def get_by_id(self, user_id: UUID) -> UserViewDTO:
        user = await self._repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(404, "User not found")

        return self._get_user_view(user)


    @retry_strategy
    async def get_by_email(self, email: str) -> UserViewDTO:
        user = await self._repository.get_by_email(email)
        self._raise_404_if_none(user)
        
        return self._get_user_view(user)


    @retry_strategy
    async def get_by_login(self, login: str) -> UserViewDTO:
        if "@" in login:
            user = await self.get_by_email(login)
        else:
            user = await self.get_by_username(login)

        return user


    @retry_strategy
    async def get_by_username(self, username: str) -> UserViewDTO:
        user = await self._repository.get_by_username(username)
        self._raise_404_if_none(user)

        return self._get_user_view(user)

    # @retry_strategy
    async def create_user(self, user_create_schema: UserCreateDTO) -> UserViewDTO:
        user = await self._repository.get_by_username(user_create_schema.username)

        if user is not None:
            raise HTTPException(409, f"User with username: {user_create_schema.username} already exists.")

        user = await self._repository.get_by_email(str(user_create_schema.email))

        if user is not None:
            raise HTTPException(409, f"User with email: {user_create_schema.email} already exists.")

        new_user = User(**user_create_schema.model_dump())
        new_user = await self._repository.create(new_user)

        return self._get_user_view(new_user)

    async def update_user(self, user_id: UUID, user_update_schema: UserUpdateDTO) -> UserViewDTO:
        user = await self._repository.get_by_id(user_id)
        self._raise_404_if_none(user)

        user = await self._repository.update(user, user_update_schema)

        return self._get_user_view(user)

    async def check_password(self, user_id: UUID, password: str) -> bool:
        user = await self._repository.get_by_id(user_id)
        self._raise_404_if_none(user)

        return bcrypt.checkpw(password.encode(), user.password)

    async def check_activation_token(self, user_id: UUID, activation_token: str) -> bool:
        user = await self._repository.get_by_id(user_id)
        self._raise_404_if_none(user)

        return bcrypt.checkpw(activation_token.encode(), user.activation_token)
