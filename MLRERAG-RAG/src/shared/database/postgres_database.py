from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core import settings


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)