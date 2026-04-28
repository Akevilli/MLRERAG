from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base

class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(nullable=False)
    is_activated: Mapped[bool] = mapped_column(nullable=False, default=False)
    activation_token: Mapped[bytes] = mapped_column(nullable=False, default=None)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now(), onupdate=func.now())

    chats: Mapped[list["Chat"]] = relationship(back_populates="owner", init=False)
