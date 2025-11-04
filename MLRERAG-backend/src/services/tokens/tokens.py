import secrets
from uuid import UUID
from datetime import timedelta, timezone
from datetime import datetime

import bcrypt
import jwt
from sqlalchemy.orm import Session

from src.repositories import RefreshTokenRepository
from src.models import RefreshToken, User
from src.core import settings


class TokenService:
    def __init__(self, rt_repository: RefreshTokenRepository):

        self.__rt_repository = rt_repository
    

    def generate_activation_token(self) -> tuple[str, bytes]:
        token = secrets.token_urlsafe(settings.ACTIVATION_TOKEN_LENGTH)
        hashed_token = bcrypt.hashpw(bytes(token, "utf-8"), bcrypt.gensalt())

        return token, hashed_token
    

    def create_refreshToken(self, owner_id: UUID, session: Session) -> RefreshToken:
        active_tokens: list[RefreshToken] = self.__rt_repository.get_active_token(owner_id, session)

        for active_token in active_tokens:
            active_token.is_revoked = True

        new_token = RefreshToken(owner_id=owner_id)
        self.__rt_repository.create(new_token, session)

        return new_token
    

    def generate_jwt_token(self, user: User) -> str:
        payload = {
            "user_id": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_LIFETIME_MIN),
            "iss": settings.JWT_ISSUER
        }

        jwt_token = jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

        return jwt_token