from fastapi import APIRouter

from .endpoints import users, auth, rag


main_router = APIRouter(prefix="/api")

routers = [
    (users.router, "/users", ["users"]),
    (auth.router, "/auth", ["auth"]),
    (rag.router, "/rag", ["rag"]),
]

for router, prefix, tags in routers:
    main_router.include_router(router, prefix=prefix, tags=tags)