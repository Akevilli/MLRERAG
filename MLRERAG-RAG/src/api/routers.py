from fastapi import APIRouter

from .endpoints import *


main_router = APIRouter()

routers = [
    (rag.router, "/rag", ["rag"])
]

for router in routers:
    main_router.include_router(router[0], prefix=router[1], tags=router[2])