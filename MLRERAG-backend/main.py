import uvicorn
from fastapi import FastAPI

from src.api import main_router
from src.core import ErrorHandler, settings, configure_logger


configure_logger()

app = FastAPI(
    openapi_extra={
        "security": [
            {
                "HTTPBearer": []
            }
        ]
    }
)

app.include_router(main_router)

ErrorHandler(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)