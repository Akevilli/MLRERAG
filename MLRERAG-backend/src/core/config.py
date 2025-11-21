from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str

    ACTIVATION_TOKEN_LENGTH: int

    REFRESH_TOKEN_LIFETIME_DAYS: int

    JWT_LIFETIME_MIN: int
    JWT_ISSUER: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    RAG_SERVICE_HOST: str
    RAG_SERVICE_PORT: int

    CONTEXT_WINDOW: int

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_TTL: int

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    @property
    def RAG_SERVICE_URL(self):
        return f"http://{self.RAG_SERVICE_HOST}:{self.RAG_SERVICE_PORT}"

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()