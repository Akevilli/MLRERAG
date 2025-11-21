from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserViewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class LoggedUserView(UserViewSchema):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: UUID