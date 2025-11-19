import bcrypt
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from email_validator import validate_email, EmailNotValidError

from src.core import retry_strategy
from src.services import UserService, EmailService, TokenService
from src.api.schemas import (
    CreateUserSchema, 
    ActivateUserSchema, 
    LoginUserSchema,
    LoginedUserView
)
from src.models import User


class AuthService:
    def __init__(
            self,
            user_service: UserService,
            email_service: EmailService,
            token_service: TokenService
        ):
        self.__user_service = user_service
        self.__email_service = email_service
        self.__token_service = token_service


    @retry_strategy
    def register(self, new_user_data: CreateUserSchema, session: Session) -> User:
        new_user_data_dict = new_user_data.model_dump()

        if new_user_data_dict["password"] != new_user_data_dict["confirm_password"]:
            raise HTTPException(400, "Passwords and Confirm password do not match!")

        token, hashed_token = self.__token_service.generate_activation_token()

        new_user_data_dict["activation_token"] = hashed_token
        new_user_data_dict['password'] = bcrypt.hashpw(bytes(new_user_data_dict["password"], "utf-8"), bcrypt.gensalt())

        new_user = User(
            username=new_user_data_dict["username"],
            email=new_user_data_dict["email"],
            password=new_user_data_dict["password"],
            activation_token=new_user_data_dict["activation_token"],
        )

        new_user = self.__user_service.create_user(new_user, session)

        self.__email_service.sent_welcome_email(new_user_data_dict["email"], token)

        return new_user


    @retry_strategy
    def activate(self, user_data: ActivateUserSchema, session: Session) -> None:
        
        try:
            validate_email(user_data.login, check_deliverability=False)
            user = self.__user_service.get_by_email(user_data.login, session)
        except EmailNotValidError:
            user = self.__user_service.get_by_username(user_data.login, session)
        
        if not bcrypt.checkpw(bytes(user_data.activation_token, "utf-8"), user.activation_token):
            raise HTTPException(400, "The provided activation token is invalid or incorrect.")
        
        user.is_activated = True


    @retry_strategy
    def login(self, user_data: LoginUserSchema, session : Session) -> LoginedUserView:

        try:
            validate_email(user_data.login, check_deliverability=False)
            user = self.__user_service.get_by_email(user_data.login, session)
        except EmailNotValidError:
            try:
                user = self.__user_service.get_by_username(user_data.login, session)
            except HTTPException:
                raise HTTPException(404,"Invalid username/email or password.")
        except HTTPException:
            raise HTTPException(404, "Invalid username/email or password.")

        if not user.is_activated:
            raise HTTPException(403, "User doesn't have required permission for login.")

        if not bcrypt.checkpw(bytes(user_data.password, "utf-8"), user.password):
            raise HTTPException(404, "Invalid username/email or password.")

        jwt_token = self.__token_service.generate_jwt_token(user)
        refresh_token = self.__token_service.create_refreshToken(user.id, session)

        result = LoginedUserView(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
            access_token=jwt_token,
            refresh_token=refresh_token.id
        )

        return result
        
