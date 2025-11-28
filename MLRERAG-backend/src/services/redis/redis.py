from uuid import UUID

from redis import Redis

from src.core import settings, retry_strategy
from src.services.messages import MessageSchema


class RedisService:
    def __init__(self, redis_store: Redis):
        self.__redis_store = redis_store

    @retry_strategy
    def append_messages(self, chat_id: UUID, messages: list[MessageSchema]):
        key = self._get_key(chat_id)

        messages_json = [message.model_dump_json() for message in messages]
        history_length = self.__redis_store.llen(key)
        message_count = len(messages)

        if history_length + message_count > settings.CONTEXT_WINDOW:
            self.__redis_store.ltrim(
                key,
                0,
                settings.CONTEXT_WINDOW - (history_length + message_count - settings.CONTEXT_WINDOW) - 1
            )

        self.__redis_store.lpush(key, *messages_json)
        self.__redis_store.expire(key, settings.REDIS_TTL)

    @retry_strategy
    def get_messages(self, chat_id: UUID) -> list[MessageSchema] | None:
        key = self._get_key(chat_id)

        if not self.__redis_store.exists(key):
            return None

        messages_json = self.__redis_store.lrange(key, 0, settings.CONTEXT_WINDOW)
        messages = [MessageSchema.model_validate_json(message) for message in messages_json]
        messages.reverse()

        return messages

    def _get_key(self, chat_id: UUID) -> str:
        return f"chat:{chat_id}:messages"
