from pydantic import BaseModel


class Chunk(BaseModel):
    document_id: str
    text: str
    chunk_index: int
