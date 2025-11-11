from .schemas import State


def should_use_rag_tool(state: State) -> str:
    if state.messages[-1].tool_calls:
        return "rag_tool_node"
    else:
        return "update_final_answer_node"