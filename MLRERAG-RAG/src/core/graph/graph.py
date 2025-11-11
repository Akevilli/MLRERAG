from langgraph.graph import StateGraph, START, END

from .schemas import State
from .nodes import orchestration_node, update_final_answer_node
from .edges import should_use_rag_tool
from .tools import rag_tool_node


workflow = StateGraph(State)

workflow.add_node("orchestration_node", orchestration_node)
workflow.add_node("rag_tool_node", rag_tool_node)
workflow.add_node("update_final_answer_node", update_final_answer_node)

workflow.add_edge(START, "orchestration_node")
workflow.add_conditional_edges(
    "orchestration_node",
    should_use_rag_tool,
    {
        "rag_tool_node": "rag_tool_node",
        "update_final_answer_node": "update_final_answer_node"
    }
)
workflow.add_edge("rag_tool_node", "orchestration_node")
workflow.add_edge("update_final_answer_node", END)

graph = workflow.compile()