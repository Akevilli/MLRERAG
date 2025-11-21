from typing import Literal, Any
import yaml

from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_xai import ChatXAI
from langchain_postgres import PGVectorStore
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from .schemas import State


class Graph:
    def __init__(self,
        llm: ChatXAI,
        vector_store: PGVectorStore,
    ):
        try:
            with open("cache/prompts.yaml", "r") as f:
                self.__prompts = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("Error: prompts/rag_prompts.yaml not found.")

        self.__vector_store = vector_store
        self.__rag_tool = Tool.from_function(
            self._rag_tool,
            description=self.__prompts["rag_tool_description"],
            name="rag_tool",
        )

        self.__final_llm = llm
        self.__orchestrator = llm.bind_tools([self.__rag_tool])

        self.__workflow = StateGraph(State)

        self.__workflow.add_node("orchestrator_node", self._orchestrator_node)
        self.__workflow.add_node("final_answer_generation_node", self._final_answer_generation_node)
        self.__workflow.add_node("rag_tool_node", ToolNode([self.__rag_tool]))

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
    def _rag_tool(self, query: str, filters: dict[str, dict[str, Any]] | None = None):
        retrieved_chunks = self.__vector_store.similarity_search(query, k=10, filter=filters)
        result = "\n".join([chunk.page_content for chunk in retrieved_chunks])
        return result


    # Nodes
    def _orchestrator_node(self, state: State) -> State:
        chat = [
            *state["messages"],
            SystemMessage(content=self.__prompts["orchestrator_system_prompt"])
        ]
        orchestrator_answer = self.__orchestrator.invoke(chat)
        print(orchestrator_answer)

        return {
            "messages": [*state["messages"], orchestrator_answer],
            "answer": state["answer"],
            "documents": state["documents"],
        }


    def _final_answer_generation_node(self, state: State) -> State:
        chat = [
            *state["messages"],
            SystemMessage(content=self.__prompts["final_generation_system_prompt"])
        ]

        final_answer = self.__final_llm.invoke(chat)

        documents = ""
        last_message = state["messages"][-1]

        if isinstance(last_message, ToolMessage):
            documents = last_message.text

        return {
            "messages": state["messages"],
            "answer": final_answer.text,
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

