import asyncio
import sys

from langchain.tools import tool
from langchain_postgres import PGEngine, PGVectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langgraph.prebuilt import ToolNode

from src.core import settings

if sys.platform == "win32":
    try:
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except ImportError:
        print("WindowsSelectorEventLoopPolicy не найден, попробуйте другую версию Python/asyncio.")

pg_engine = PGEngine.from_connection_string(f"postgresql+psycopg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
vector_store = PGVectorStore.create_sync(
    pg_engine,
    table_name="chunks",
    id_column="id",
    content_column="text",
    embedding_service=HuggingFaceEmbeddings(
        model_name=settings.EMBEDDER_NAME,
        model_kwargs={'device': settings.DEVICE},
        encode_kwargs={'normalize_embeddings': True}
    ),
    embedding_column="embedding"
)


# Tools
@tool(description="RAG tool where model can find any information about ML/DL.")
def rag_tool(query: str) -> str:
    retrieved_chunks = vector_store.similarity_search(query, k=10)
    result = "".join([chunk.page_content for chunk in retrieved_chunks])

    return result


# Tool nodes
rag_tool_node = ToolNode([rag_tool])