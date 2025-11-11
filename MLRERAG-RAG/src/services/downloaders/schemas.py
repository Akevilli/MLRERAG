from datetime import datetime

from pydantic import BaseModel


class DocumentInfo(BaseModel):
    id: str
    title: str
    summary: str
    source_url: str
    published_at: datetime
