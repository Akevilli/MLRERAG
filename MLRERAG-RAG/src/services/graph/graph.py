from typing import Literal

from langchain_core.messages import ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_postgres import PGVectorStore
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from .schemas import State



class Graph:
    def __init__(self,
        llm: ChatOpenAI,
        vector_store: PGVectorStore,
    ):
        self.__final_llm = llm
        self.__orchestrator = llm.bind_tools([self._rag_tool])

        self.__vector_store = vector_store

        self.__workflow = StateGraph(State)

        self.__workflow.add_node("orchestrator_node", self._orchestrator_node)
        self.__workflow.add_node("final_answer_generation_node", self._final_answer_generation_node)
        self.__workflow.add_node("rag_tool_node", ToolNode([self._rag_tool]))

        self.__workflow.add_edge(START, "orchestrator_node")
        self.__workflow.add_conditional_edges(
            "orchestrator_node",
            self._use_rag_tool,
            {
                "rag_tool_node": "rag_tool_node",
                "final_answer_generation_node": "final_answer_generation_node",
            }
        )
        self.__workflow.add_edge("rag_tool_node", "final_answer_generation_node")
        self.__workflow.add_edge("final_answer_generation_node", END)

        self.__graph = self.__workflow.compile()


    # Tools
    @tool(description="RAG tool where model can find any information about ML/DL.")
    def _rag_tool(self, query: str):
        retrieved_chunks = self.__vector_store.similarity_search(query, k=10)
        result = "".join([chunk.page_content for chunk in retrieved_chunks])
        return result


    # Nodes
    def _orchestrator_node(self, state: State) -> State:
        orchestrator_answer = self.__orchestrator.invoke(state["messages"])

        return {
            "messages": [*state["messages"], orchestrator_answer],
            "answer": state["answer"],
            "documents": state["documents"],
        }


    def _final_answer_generation_node(self, state: State) -> State:
        final_answer = self.__final_llm.invoke(state["messages"])

        documents = ""
        last_message = final_answer["messages"][-1]

        if isinstance(last_message, ToolMessage):
            documents = last_message.text

        return {
            "messages": state["messages"],
            "answer": final_answer["answer"],
            "documents": documents,
        }


    # Edges
    def _use_rag_tool(self, state: State) -> Literal["rag_tool_node", "final_answer_generation_node"]:
        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "rag_tool_node"

        return "final_answer_generation_node"


    def invoke(self, state: State) -> State:
        return self.__graph.invoke(state)

