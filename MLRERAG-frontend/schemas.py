from typing import Literal, Optional, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    API_HOST: str
    API_PORT: int

    @property
    def API_URL(self) -> str:
        return f"http://{self.API_HOST}:{self.API_PORT}"


class Chat(BaseModel):
    id: str | None = None
    title: str | None = None

class Message(BaseModel):
    text: str
    type: Literal["user", "tool", "assistant"]

class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str

class User(TokensSchema):
    id: str
    username: str
    email: str

class GeneratedResponse(BaseModel):
    messages: List[Message]
    chat: Chat

class PaginationRequest(BaseModel):
    page: int = Field(description="Current page number", ge=0)
    page_size: int = Field(description="Number of items in a single page", ge=0)
    sort: Literal["asc", "desc"] = Field(description="Sort order")


class PaginationMetadata(BaseModel):
    total: int = Field(description="Total items", ge=0)
    next: Optional[PaginationRequest] = Field(description="Url to next page")
    previous: Optional[PaginationRequest] = Field(description="Url to previous page")

class PaginatedAPIResponse[T: BaseModel](BaseModel):
    items: List[T]
    metadata: PaginationMetadata

class Response[T: Optional[BaseModel]](BaseModel):
    message: Optional[str]
    is_success: bool
    data: Optional[T]

    @classmethod
    def success(cls, data: T, message: str = None) -> "Response":
        return cls(data=data, message=message, is_success=True)

    @classmethod
    def fail(cls, message: str) -> "Response":
        return cls(data=None, message=message, is_success=False)


settings = Settings()