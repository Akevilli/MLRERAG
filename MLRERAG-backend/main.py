from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler
from src.dependencies import get_logger


app = FastAPI()

app.include_router(main_router)

ErrorHandler(app, get_logger())