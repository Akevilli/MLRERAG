from redis import ConnectionPool

from src.core import settings


pool = ConnectionPool().from_url(settings.REDIS_URL)