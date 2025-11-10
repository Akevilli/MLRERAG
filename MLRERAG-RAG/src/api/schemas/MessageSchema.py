from pydantic import BaseModel


class MessageSchema(BaseModel):
    content: str
    is_users: bool