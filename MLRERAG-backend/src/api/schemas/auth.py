import re
from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.core import settings


class CreateUserSchema(BaseModel):
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


class ActivateUserSchema(BaseModel):

    login: EmailStr | str
    activation_token: Annotated[str, Field(
        min_length=settings.ACTIVATION_TOKEN_LENGTH + 2,
        max_length=settings.ACTIVATION_TOKEN_LENGTH + 2
    )]


class LoginUserSchema(BaseModel):

    login: EmailStr | str
    password: str


class UpdateJWTSchema(BaseModel):

    user_id: UUID
    refresh_token: UUID


class RefreshJWTSchema(BaseModel):

    refresh_token: UUID
    access_token: str