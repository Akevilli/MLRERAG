from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    API_URL: str


class Chat(BaseModel):
    id: str | None = None
    title: str | None = None


class Message(BaseModel):
    content: str
    is_users: bool


class User(BaseModel):
    id: str
    username: str
    email: str
    access_token: str
    refresh_token: str


class GeneratedResponse(BaseModel):
    answer: str
    documents: str
    chat: Chat


class PaginatedAPIResponse[T: BaseModel](BaseModel):
    items: list[T]
    page: int
    total: int


class Response[T: BaseModel | None](BaseModel):
    message: str | None
    is_success: bool
    data: T | None

    @classmethod
    def success(cls, data: T, message: str = None) -> "Response":
        return cls(data=data, message=message, is_success=True)

    @classmethod
    def fail(cls, message: str) -> "Response":
        return cls(data=None, message=message, is_success=False)


settings = Settings()