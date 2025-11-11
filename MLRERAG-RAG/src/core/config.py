from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Llama
    LLAMA_PARSER_API_KEY: str

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    # Models
    EMBEDDER_NAME: str
    DEVICE: str

    # API_KEYS
    OPENAI_API_KEY: str

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
                f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}")


settings = Settings()