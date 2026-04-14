from neo4j import AsyncGraphDatabase

from src.core import settings


neo4j_client = AsyncGraphDatabase.driver(
    uri=f"{settings.GRAPH_DB_HOST}:{settings.GRAPH_DB_PORT}",
    auth=(settings.GRAPH_DB_USER, settings.GRAPH_DB_PASSWORD),
)
