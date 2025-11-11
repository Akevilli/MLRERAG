from ..BaseRepository import BaseRepository
from src.models import Chat


class ChatRepository(BaseRepository):
    def __init__(self):
        super().__init__(Chat)