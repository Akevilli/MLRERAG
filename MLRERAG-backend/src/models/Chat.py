from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func

from .Base import Base


class Chat(Base):
    __tablename__ = 'chats'

    title: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(back_populates="chats", init=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", init=False)