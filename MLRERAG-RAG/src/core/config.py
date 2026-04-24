import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    BASE_DIR: Path = Path(__file__).parent.parent.parent

    RAG_PORT: int
    BATCH_SIZE: int
    CHUNK_SIZE: int
    OVERLAP: int

    # Llama
    LLAMA_PARSER_API_KEY: str

    # Ollama
    OLLAMA_HOST: str
    OLLAMA_PORT: int

    # Grobid
    GROBID_HOST: str
    GROBID_PORT: int

    # Databases
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER_RAG: str
    POSTGRES_PASSWORD_RAG: str
    POSTGRES_DATABASE: str

    VECTOR_DB_HOST: str
    VECTOR_DB_PORT: int
    VECTOR_DB_COLLECTION: str

    GRAPH_DB_HOST: str
    GRAPH_DB_PORT: int
    GRAPH_DB_USER: str
    GRAPH_DB_PASSWORD: str
    GRAPH_DB_DATABASE: str

    # Models
    EMBEDDER_MODEL: str
    EMBEDDER_DEVICE: str
    EMBEDDER_BATCH_SIZE: int
    EMBEDDING_DIM: int

    TAGGER_MODEL: str
    TAGGER_API_KEY: str

    RERANKER_NAME: str
    RERANKER_DEVICE: str

    # API_KEYS
    GROK_API_KEY: str
    GROK_MODEL: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER_RAG}:{self.POSTGRES_PASSWORD_RAG}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")


settings = Settings()