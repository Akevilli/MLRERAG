import logging
from logging import Logger
from typing import Generator, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal
from .repositories import (
    RefreshTokenRepository,
    UserRepository
)
from .services import (
    AuthService,
    UserService,
    EmailService,
    TokenService
)


# DB
_session = SessionLocal()

# Logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.FileHandler("app.log", mode="a"))

# Repositories
_refresh_token_repository = RefreshTokenRepository()
_user_repository = UserRepository()

# Services
_user_service = UserService(_user_repository)
_email_service = EmailService()
_token_service = TokenService(_refresh_token_repository)
_auth_service = AuthService(_user_service, _email_service, _token_service)


def get_session() -> Generator[Session, Any, None]:
    try:
        yield _session
        _session.commit()

    except SQLAlchemyError:
        _session.rollback()
        raise

    finally:
        _session.close()


def  get_user_service() -> UserService:
    return _user_service

def get_email_service() -> EmailService:
    return _email_service

def get_token_service() -> TokenService:
    return _token_service

def get_auth_service() -> AuthService:
    return _auth_service

def get_logger() -> Logger:
    return _logger



