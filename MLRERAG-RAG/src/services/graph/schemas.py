from typing import Annotated, TypedDict, List
import operator

from langchain_core.messages import AnyMessage


class State(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    answer: str
    documents: str