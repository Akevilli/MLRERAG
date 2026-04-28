import bcrypt
from fastapi.exceptions import HTTPException
from loguru import logger

from .schemas import (
    RegisterUserDTO,
    ActivateUserDTO,
    LoginUserResponseDTO,
    LoginUserDTO,
    RefreshJWTDTO,
    RefreshJWTResponseDTO
)
from src.core import retry_strategy
from src.services import (
    UserService,
    EmailService,
    TokenService,
    UserCreateDTO,
    UserUpdateDTO,
    UserViewDTO
)


class AuthService:
    def __init__(
            self,
            user_service: UserService,
            email_service: EmailService,
            token_service: TokenService
    ):
        self._user_service = user_service
        self._email_service = email_service
        self._token_service = token_service

    # @retry_strategy
    async def register(self, new_user_data_schema: RegisterUserDTO) -> UserViewDTO:
        new_user_data = new_user_data_schema.model_dump()

        if new_user_data["password"] != new_user_data["confirm_password"]:
            raise HTTPException(400, "Passwords and Confirm password do not match!")

        token, hashed_token = self._token_service.generate_activation_token()

        new_user_data["activation_token"] = hashed_token
        new_user_data["password"] = bcrypt.hashpw(new_user_data_schema.password.encode(), bcrypt.gensalt())

        new_user = UserCreateDTO(**new_user_data)
        new_user = await self._user_service.create_user(new_user)
        logger.info(f"New user was created: {new_user.email}")

        await self._email_service.sent_welcome_email(str(new_user.email), token)
        logger.info(f"Welcome email was sent to: {new_user.email}")

        return new_user

    @retry_strategy
    async def activate(self, activate_user_dto: ActivateUserDTO) -> None:
        user_view = await self._user_service.get_by_login(activate_user_dto.login)

        if not await self._user_service.check_activation_token(user_view.id, activate_user_dto.activation_token):
            raise HTTPException(400, "The provided activation token is invalid or incorrect.")

        update_user_schema = UserUpdateDTO(is_activated=True)
        await self._user_service.update_user(user_view.id, update_user_schema)

    @retry_strategy
    async def login(self, login_schema: LoginUserDTO) -> LoginUserResponseDTO:
        user_view = await self._user_service.get_by_login(login_schema.login)

        if not user_view.is_activated:
            raise HTTPException(403, "User doesn't have required permission for login.")

        if not await self._user_service.check_password(user_view.id, login_schema.password):
            raise HTTPException(404, "Invalid username/email or password.")

        jwt_token = self._token_service.generate_jwt_token(user_view.id)
        refresh_token = await self._token_service.create_refresh_token(user_view.id)

        result = LoginUserResponseDTO(
            **user_view.model_dump(),
            access_token=jwt_token,
            refresh_token=refresh_token.id
        )

        return result

    @retry_strategy
    async def refresh_jwt(self, refresh_jwt_request_dto: RefreshJWTDTO) -> RefreshJWTResponseDTO:
        if not await self._token_service.check_refresh_token(**refresh_jwt_request_dto.model_dump()):
            raise HTTPException(403, "Refresh token is invalid.")

        user_view = await self._user_service.get_by_id(refresh_jwt_request_dto.user_id)

        jwt_token = self._token_service.generate_jwt_token(user_view.id)
        refresh_token = await self._token_service.create_refresh_token(user_view.id)

        return RefreshJWTResponseDTO(access_token=jwt_token, refresh_token=refresh_token.id)
