from src.shared.database import Base
from src.shared.database import engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)