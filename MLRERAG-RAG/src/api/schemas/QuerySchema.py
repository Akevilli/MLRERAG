from pydantic import BaseModel

from .MessageSchema import MessageSchema


class QuerySchema(BaseModel):
    messages: list[MessageSchema]