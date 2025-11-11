import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token is expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
