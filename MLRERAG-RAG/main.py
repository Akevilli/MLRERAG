from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler, _logger


app = FastAPI()

app.include_router(main_router)

ErrorHandler(app, logger=_logger)