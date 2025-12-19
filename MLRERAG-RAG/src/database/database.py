from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core import settings


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={'options': '-c client_encoding=UTF8'})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)