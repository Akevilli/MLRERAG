from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Llama
    LLAMA_PARSER_API_KEY: str

    # Database
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER_RAG: str
    POSTGRES_PASSWORD_RAG: str
    POSTGRES_DATABASE: str

    # Models
    EMBEDDER_NAME: str
    EMBEDDER_DEVICE: str

    RERANKER_NAME: str
    RERANKER_DEVICE: str

    # API_KEYS
    GROK_API_KEY: str
    GROK_MODEL: str

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (f"postgresql+psycopg2://{self.POSTGRES_USER_RAG}:{self.POSTGRES_PASSWORD_RAG}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    @property
    def PGVECTOR_DATABASE_URI(self):
        return (f"postgresql+psycopg://{self.POSTGRES_USER_RAG}:{self.POSTGRES_PASSWORD_RAG}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")


settings = Settings()