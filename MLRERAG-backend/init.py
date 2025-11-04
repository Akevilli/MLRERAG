from src.models import Base
from src.database import engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
