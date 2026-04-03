from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler, configure_logger


configure_logger()

app = FastAPI()

app.include_router(main_router)

ErrorHandler(app)