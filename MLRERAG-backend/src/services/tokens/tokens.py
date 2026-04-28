import secrets
from uuid import UUID
from datetime import timedelta, timezone
from datetime import datetime

import bcrypt
import jwt

from src.shared.repositories import RefreshTokenRepository
from src.shared.databases.postgres.models import RefreshToken
from src.core import settings, retry_strategy


class TokenService:
    def __init__(self, rt_repository: RefreshTokenRepository):

        self._rt_repository = rt_repository
    
    @staticmethod
    def generate_activation_token() -> tuple[str, bytes]:
        token = secrets.token_urlsafe(settings.ACTIVATION_TOKEN_LENGTH)
        hashed_token = bcrypt.hashpw(token.encode(), bcrypt.gensalt())

        return token, hashed_token


    @retry_strategy
    async def create_refresh_token(self, owner_id: UUID) -> RefreshToken:
        active_tokens = await self._rt_repository.get_active_token(owner_id)

        for active_token in active_tokens:
            active_token.is_revoked = True

        new_token = RefreshToken(owner_id=owner_id)
        await self._rt_repository.create(new_token)

        return new_token


    @retry_strategy
    async def check_refresh_token(self, user_id: UUID, refresh_token: UUID) -> bool:
        active_token = await self._rt_repository.get_active_by_user_id_and_token(user_id, refresh_token)

        if active_token is None:
            return False

        return True


    @staticmethod
    def generate_jwt_token(user_id: UUID) -> str:
        payload = {
            "user_id": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_LIFETIME_MIN),
            "iss": settings.JWT_ISSUER
        }

        jwt_token = jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

        return jwt_token