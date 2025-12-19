import logging
from logging import Logger
from typing import Generator, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from redis import Redis

from .database import SessionLocal
from .redis import pool
from .repositories import (
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


# Redis store
_redis = Redis(decode_responses=True).from_pool(pool)

# DB
_session = SessionLocal()

# Logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.FileHandler("app.log", mode="a"))

# Repositories
_refresh_token_repository = RefreshTokenRepository()
_user_repository = UserRepository()
_chat_repository = ChatRepository()
_message_repository = MessageRepository()

# Services
_redis_service = RedisService(_redis)
_user_service = UserService(_user_repository)
_email_service = EmailService()
_token_service = TokenService(_refresh_token_repository)
_auth_service = AuthService(_user_service, _email_service, _token_service)
_chat_service = ChatService(_chat_repository)
_message_service = MessageService(_message_repository, _chat_service)
_rag_service = RAGService(_chat_service, _message_service, _redis_service)


def get_session() -> Generator[Session, Any, None]:
    try:
        yield _session
        _session.commit()

    except SQLAlchemyError:
        _session.rollback()
        raise

    finally:
        _session.close()


def get_user_service() -> UserService:
    return _user_service

def get_email_service() -> EmailService:
    return _email_service

def get_token_service() -> TokenService:
    return _token_service

def get_auth_service() -> AuthService:
    return _auth_service

def get_logger() -> Logger:
    return _logger

def get_chat_service() -> ChatService:
    return _chat_service

def get_message_service() -> MessageService:
    return _message_service

def get_rag_service() -> RAGService:
    return _rag_service


