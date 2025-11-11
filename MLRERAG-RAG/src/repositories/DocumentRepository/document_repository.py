from ..BaseRepository import BaseRepository
from src.models import Document


class DocumentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Document)