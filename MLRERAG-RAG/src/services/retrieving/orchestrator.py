from typing import List

import yaml
from langchain_xai import ChatXAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from loguru import logger

from .search_engine import SearchEngine
from .schemas import AgentState
from .lib import message_dto_to_message, message_to_message_dto
from src.shared.embedders import Embedder
from src.shared.schemas import ChatHistory


class RetrievingService:
    def __init__(
            self,
            embedder: Embedder,
            search_engine: SearchEngine,
            llm: ChatXAI
    ):
        with open("cache/prompts.yaml", "r") as file:
            prompts = yaml.safe_load(file)
            self._agent_system_prompt = prompts["agent_system_prompt"]
            self._rag_tool_description = prompts["rag_tool_description"]

        self._embedder = embedder
        self._search_engine = search_engine
        tools = [self.create_rag_tool()]
        self._llm = llm.bind_tools(tools)

        workflow = StateGraph(AgentState)
        tool_node = ToolNode(tools)

        workflow.add_node("agent", self.llm)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")

        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges(
            "agent",
            self.agent_tool_edge,
            {
                "tools": "tools",
                END: END
            }
        )

        self.agent = workflow.compile()

    async def generate_answer(self, history: ChatHistory) -> ChatHistory:
        messages = [
            SystemMessage(content=self._agent_system_prompt),
            *[
                message_dto_to_message(message)
                for message in history.messages
            ]
        ]
        logger.info(f"Request: {messages[-1].text}")

        init_state = AgentState(messages=messages)
        agent_response = await self.agent.ainvoke(
            init_state,
            config=RunnableConfig(
                configurable={
                    "recursion_limit": 10
                }
            )
        )

        tool_messages = [message for message in agent_response["messages"][2:] if isinstance(message, ToolMessage)]
        result_messages = tool_messages + [agent_response["messages"][-1]]

        return ChatHistory(
            messages=[
                message_to_message_dto(message)
                for message in result_messages
            ]
        )

    # nodes
    async def llm(self, state: AgentState):
        response = await self._llm.ainvoke(state.messages)
        return {"messages": response}


    # tools
    def create_rag_tool(self):
        @tool(description=self._rag_tool_description)
        async def _rag_tool(queries: List[str], tags: List[str]):
            logger.info(
                f"_rag_tool was executed with parameters; queries: {queries}, tags: {tags}"
            )

            embedded_queries = await self._embedder.embed_query(queries)
            retrieved_documents = await self._search_engine.search(embedded_queries, tags)

            logger.info(f"Retrieved {len(retrieved_documents)} documents.")

            return "\n\n\n".join([str(retrieved_document) for retrieved_document in retrieved_documents])

        return _rag_tool

    @staticmethod
    def agent_tool_edge(state: AgentState):
        if state.messages[-1].tool_calls:
            return "tools"

        return END
