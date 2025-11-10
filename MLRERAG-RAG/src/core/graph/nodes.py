from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage

from src.core.config import settings
from .schemas import State
from .tools import rag_tool


llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
orchestration_llm = llm.bind_tools([rag_tool])

def orchestration_node(state: State) -> State:
    orchestration_response = orchestration_llm.invoke(state.messages)

    return State(
        answer=state.answer,
        messages=[*state.messages, orchestration_response],
        documents=state.documents,
    )


def update_final_answer_node(state: State) -> State:
    """
    Extracts the final answer content from the last message
    and returns a new State with the 'answer' field updated.
    """
    final_message = state.messages[-1]
    tool_message = state.messages[-2]

    final_answer_text = ""
    documents: str = ""

    if isinstance(final_message, AIMessage):
        final_answer_text = final_message.content

    if isinstance(tool_message, ToolMessage):
         documents = tool_message.content

    return State(
        answer=final_answer_text,
        messages=state.messages,
        documents=documents,
    )




