from uuid import UUID

from redis import Redis

from src.core import settings, retry_strategy
from src.services.messages import MessageViewDTO


class RedisService:
    def __init__(self, redis_store: Redis):
        self._redis_store = redis_store

    @retry_strategy
    async def append_messages(self, chat_id: UUID, messages: list[MessageViewDTO]):
        key = self._get_key(chat_id)

        messages_json = [message.model_dump_json() for message in messages]
        history_length = await self._redis_store.llen(key)
        message_count = len(messages)

        if history_length + message_count > settings.CONTEXT_WINDOW:
            await self._redis_store.ltrim(
                key,
                0,
                settings.CONTEXT_WINDOW - (history_length + message_count - settings.CONTEXT_WINDOW) - 1
            )

        await self._redis_store.lpush(key, *messages_json)
        await self._redis_store.expire(key, settings.REDIS_TTL)

    @retry_strategy
    async def get_messages(self, chat_id: UUID) -> list[MessageViewDTO] | None:
        key = self._get_key(chat_id)

        if not await self._redis_store.exists(key):
            return None

        messages_json = await self._redis_store.lrange(key, 0, settings.CONTEXT_WINDOW)
        messages = [MessageViewDTO.model_validate_json(message) for message in messages_json]
        messages.reverse()

        return messages

    @staticmethod
    def _get_key(chat_id: UUID) -> str:
        return f"chat:{chat_id}:messages"
