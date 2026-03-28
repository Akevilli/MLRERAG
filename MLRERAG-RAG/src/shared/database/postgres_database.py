from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core import settings


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={'options': '-c client_encoding=UTF8'})
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)