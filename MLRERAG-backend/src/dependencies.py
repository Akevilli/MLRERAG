from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from redis.asyncio import Redis
from httpx import AsyncClient

from src.shared.databases import SessionLocal, pool
from src.shared.repositories import (
    RefreshTokenRepository,
    UserRepository,
    ChatRepository,
    MessageRepository
)
from .services import (
    AuthService,
    UserService,
    EmailService,
    TokenService,
    ChatService,
    MessageService,
    RAGService,
    RedisService
)

# httpx
_http_client = AsyncClient()

# Redis store
_redis = Redis(decode_responses=True).from_pool(pool)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    _session = SessionLocal()
    try:
        yield _session
        await _session.commit()

    except SQLAlchemyError:
        await _session.rollback()
        raise

    finally:
        await _session.close()

# Repos
def _get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

def _get_refresh_token_repository(session: AsyncSession = Depends(get_session)) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)

def _get_chat_repository(session: AsyncSession = Depends(get_session)) -> ChatRepository:
    return ChatRepository(session)

def _get_message_repository(session: AsyncSession = Depends(get_session)) -> MessageRepository:
    return MessageRepository(session)

# Services
async def get_user_service(user_repository: UserRepository = Depends(_get_user_repository)) -> UserService:
    return UserService(user_repository)

async def get_redis_service() -> RedisService:
    return RedisService(_redis)

async def get_email_service() -> EmailService:
    return EmailService()

def get_token_service(refresh_token_repository: RefreshTokenRepository = Depends(_get_refresh_token_repository)) -> TokenService:
    return TokenService(refresh_token_repository)

async def get_auth_service(
        user_service: UserService = Depends(get_user_service),
        email_service: EmailService = Depends(get_email_service),
        token_service: TokenService = Depends(get_token_service)
) -> AuthService:
    return AuthService(user_service, email_service, token_service)

async def get_chat_service(chat_repository: ChatRepository = Depends(_get_chat_repository)) -> ChatService:
    return ChatService(chat_repository)

async def get_message_service(
        message_repository: MessageRepository = Depends(_get_message_repository),
        chat_service: ChatService = Depends(get_chat_service)
) -> MessageService:
    return MessageService(message_repository, chat_service)

async def get_rag_service(
        chat_service: ChatService = Depends(get_chat_service),
        message_service: MessageService = Depends(get_message_service),
        redis_service: RedisService = Depends(get_redis_service)
) -> RAGService:
    return RAGService(_http_client, chat_service, message_service, redis_service)


