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
    name: str | None = None


class Message(BaseModel):
    content: str
    is_users: bool


settings = Settings()