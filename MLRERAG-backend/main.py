from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler
from src.dependencies import get_logger


app = FastAPI(
    openapi_extra={
        "security": [
            {
                "HTTPBearer": [] # <--- Changed from OAuth2PasswordBearer
            }
        ]
    }
)

app.include_router(main_router)

ErrorHandler(app, get_logger())