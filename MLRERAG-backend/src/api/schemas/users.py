from uuid import UUID
from datetime import datetime
from typing import Annotated
import re

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


class UserViewSchema(BaseModel):

    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class ActivateUserSchema(BaseModel):

    login: EmailStr | str
    activation_token: Annotated[str, Field(
        min_length=settings.ACTIVATION_TOKEN_LENGTH + 2,
        max_length=settings.ACTIVATION_TOKEN_LENGTH + 2
    )]


class LoginUserSchema(BaseModel):

    login: EmailStr | str
    password: str


class LoginedUserView(UserViewSchema):

    access_token: str
    refresh_token: UUID