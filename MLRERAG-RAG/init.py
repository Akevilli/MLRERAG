import asyncio
import sys
import selectors

from src.shared.database import Base, engine


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    if sys.platform == 'win32':
        loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.run(init(), loop_factory=loop_factory)
    else:
        asyncio.run(init())