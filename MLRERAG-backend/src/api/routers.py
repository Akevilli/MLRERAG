from fastapi import APIRouter

from .endpoints import users, auth


main_router = APIRouter(prefix="/api")

routers = [
    (users.router, "/users", ["users"]),
    (auth.router, "/auth", ["auth"])
]

for router, prefix, tags in routers:
    main_router.include_router(router, prefix=prefix, tags=tags)