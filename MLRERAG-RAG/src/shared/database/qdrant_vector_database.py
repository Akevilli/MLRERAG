from qdrant_client import AsyncQdrantClient, models

from src.core.config import settings


qdrant_client = AsyncQdrantClient(
    host=settings.VECTOR_DB_HOST,
    port=settings.VECTOR_DB_PORT,
)