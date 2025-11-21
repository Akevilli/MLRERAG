from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from src.core import retry_strategy
from src.repositories import UserRepository
from src.models import User


class UserService:
    def __init__(self, repository: UserRepository):
        self.__repository = repository


    @retry_strategy
    def get_by_id(self, user_id: UUID, session: Session) -> User | None:
        user = self.__repository.get_by_id(user_id, session)

        if user is None:
            raise HTTPException(404, "User not found")

        return user


    @retry_strategy
    def get_by_email(self, email: str, session: Session) -> User | None:
        user = self.__repository.get_by_email(email, session)

        if user is None:
            raise HTTPException(404, "User not found")
        
        return user


    @retry_strategy
    def get_by_username(self, username: str, session: Session) -> User | None:
        user = self.__repository.get_by_username(username, session)

        if user is None:
            raise HTTPException(404, "User not found")

        return user


    @retry_strategy
    def create_user(self, new_user: User, session: Session) -> User | None:
        user = self.__repository.get_by_username(new_user.username, session)

        if user is not None:
            raise HTTPException(409, f"User with username: {new_user.username} already exists.")

        user = self.__repository.get_by_email(new_user.email, session)

        if user is not None:
            raise HTTPException(409, f"User with email: {new_user.email} already exists.")

        user = self.__repository.create(new_user, session)

        return user
