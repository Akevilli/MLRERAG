import asyncio
import sys
import selectors

from src.shared.databases.postgres.models import Base
from src.shared.databases import engine


async def init():
    # Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    if sys.platform == 'win32':
        loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.run(init(), loop_factory=loop_factory)
    else:
        asyncio.run(init())
