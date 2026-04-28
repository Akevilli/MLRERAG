from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from src.services.users import UserViewDTO


class RegisterUserDTO(BaseModel):
    username: str = Field(description="New user's username.")
    email: EmailStr = Field(description="New user's email address.")
    password: str = Field(description="New user's password.")
    confirm_password: str = Field(description="New user's confirmation password.")

class ActivateUserDTO(BaseModel):
    login: EmailStr | str = Field(description="User's name/email.")
    activation_token: str = Field(description="User's activation token.")

class RefreshJWTDTO(BaseModel):
    user_id: UUID = Field(description="User's ID")
    refresh_token: UUID = Field(description="User's refresh Token")

class RefreshJWTResponseDTO(BaseModel):
    refresh_token: UUID
    access_token: str

class LoginUserDTO(BaseModel):
    login: EmailStr | str = Field(description="User's name/email.")
    password: str = Field(description="User's password.")

class LoginUserResponseDTO(UserViewDTO, RefreshJWTResponseDTO):
    pass
