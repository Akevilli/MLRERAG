from fastapi import APIRouter

from .endpoints import users, auth, rag, chats, messages


main_router = APIRouter(prefix="/api")

routers = [
    (users.router, "/users", ["users"]),
    (auth.router, "/auth", ["auth"]),
    (rag.router, "/rag", ["rag"]),
    (chats.router, "/chats", ["chats"]),
    (messages.router, "/messages", ["messages"]),
]

for router, prefix, tags in routers:
    main_router.include_router(router, prefix=prefix, tags=tags)