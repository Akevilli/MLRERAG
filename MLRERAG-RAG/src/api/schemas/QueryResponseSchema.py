from pydantic import BaseModel


class QueryResponseSchema(BaseModel):
    answer: str
    documents: str