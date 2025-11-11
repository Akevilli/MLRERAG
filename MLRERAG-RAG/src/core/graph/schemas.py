from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from typing import Annotated
import operator


class State(BaseModel):
    messages: Annotated[list[BaseMessage], operator.add] = Field(
        default_factory=list,
        description="The full conversation history (Human, AI, Tool messages)."
    )

    answer: str = Field("", description="Generated final answer.")
    documents: str = Field("", description="Retrieved documents.")
