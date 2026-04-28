from typing import Literal
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .Base import Base


class Message(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, init=False)
    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("chats.id", ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    type: Mapped[Literal["assistant", "user"]] = mapped_column(nullable=False, default=True)
    chat: Mapped["Chat"] = relationship(back_populates="messages", init=False)