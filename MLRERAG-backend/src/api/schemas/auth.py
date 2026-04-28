import re
from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.core import settings
from src.services.auth import (
    ActivateUserDTO,
    RegisterUserDTO,
    LoginUserDTO,
    RefreshJWTDTO
)


class CreateUserRequestSchema(BaseModel):
    model_config = ConfigDict(
        regex_engine="python-re"
    )

    username: str
    email: EmailStr
    password: Annotated[str, Field(
        min_length=6,
        max_length=64,
        pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&_;])[A-Za-z\d@$!%*#?&_;]{8,}$")
    )]
    confirm_password: str

    def to_dto(self) -> RegisterUserDTO:
        return RegisterUserDTO(**self.model_dump())


class ActivateUserRequestSchema(BaseModel):
    login: EmailStr | str
    activation_token: Annotated[str, Field(
        min_length=settings.ACTIVATION_TOKEN_LENGTH + 2,
        max_length=settings.ACTIVATION_TOKEN_LENGTH + 2
    )]

    def to_dto(self) -> ActivateUserDTO:
        return ActivateUserDTO(**self.model_dump())


class LoginUserRequestSchema(BaseModel):
    login: EmailStr | str
    password: str

    def to_dto(self) -> LoginUserDTO:
        return LoginUserDTO(**self.model_dump())


class RefreshJWTRequestSchema(BaseModel):
    user_id: UUID
    refresh_token: UUID

    def to_dto(self) -> RefreshJWTDTO:
        return RefreshJWTDTO(**self.model_dump())
