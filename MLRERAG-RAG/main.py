import uvicorn
from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler, configure_logger, settings


configure_logger()

app = FastAPI()

app.include_router(main_router)
ErrorHandler(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)