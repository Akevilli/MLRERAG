from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserBaseDTO(BaseModel):
    username: str = Field(description="User's name.")
    email: EmailStr = Field(description="User's email.")

class UserCreateDTO(UserBaseDTO):
    password: bytes = Field(description="User's password.")
    activation_token: bytes = Field(description="User's activation token.")

class UserViewDTO(UserBaseDTO):
    id: UUID = Field(description="User's identifier.")
    is_activated: bool = Field(description="Flag which shows user's activation status.")


class UserUpdateDTO(BaseModel):
    username: Optional[str] = Field(default=None, description="User's name.")
    email: Optional[EmailStr] = Field(default=None, description="User's email.")
    password: Optional[str] = Field(default=None, description="User's password.")
    is_activated: Optional[bool] = Field(default=None, description="Flag which shows user's activation status.")
    activation_token: Optional[bytes] = Field(default=None, description="User's activation token.")
