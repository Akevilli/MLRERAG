import sys
import asyncio
from typing import AsyncGenerator, Any, Optional
from logging import Logger

import arxiv
import httpx
import instructor
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_xai import ChatXAI
from langchain_postgres import PGVectorStore, PGEngine
from llama_cloud_services import LlamaParse
from langchain_experimental.text_splitter import SemanticChunker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from FlagEmbedding import FlagReranker

from src.shared.database import SessionLocal
from src.shared.repositories import *
from .services import *
from .services.graph import Graph
from .core import settings, _logger
from .services.metadata import TagsAndEntitiesExtractor
from .services.uploading.parsers import grobid_parser

if sys.platform == "win32":
    try:
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except ImportError:
        print("WindowsSelectorEventLoopPolicy не найден, попробуйте другую версию Python/asyncio.")


# Logger
def get_logger() -> Logger:
    return _logger

# Clients
_arxiv_client = arxiv.Client()
_httpx_client = httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"})


# arXiv
_arxiv_provider = ArxivProvider(arxiv_client=_arxiv_client, httpx_client=_httpx_client)

# Models
# _embedder = HuggingFaceEmbeddings(
#     model_name=settings.EMBEDDER_NAME,
#     model_kwargs={'device': settings.EMBEDDER_DEVICE},
#     encode_kwargs={'normalize_embeddings': True}
# )
# _llama_parse = LlamaParse(api_key=settings.LLAMA_PARSER_API_KEY, num_workers=1, verbose=False, language="en")
_grok_llm = ChatXAI(
    api_key=settings.GROK_API_KEY,
    model=settings.GROK_MODEL
)
# _reranker = FlagReranker(
#     model_name_or_path=settings.RERANKER_NAME,
#     use_gpu=True,
#     device_type=settings.RERANKER_DEVICE,
# )


# PGVectorStore
# _pg_engine = PGEngine.from_connection_string(settings.SQLALCHEMY_DATABASE_URI)
# _vector_store = PGVectorStore.create_sync(
#     _pg_engine,
#     table_name="chunks",
#     id_column="id",
#     content_column="text",
#     embedding_column="embedding",
#     metadata_json_column="chunk_metadata",
#     embedding_service=_embedder,
# )

# DB
_session = SessionLocal()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        yield _session
        await _session.commit()

    except SQLAlchemyError:
        await _session.rollback()
        raise

    finally:
        await _session.close()

# papers
def get_paper_repository(session: AsyncSession = Depends(get_session)) -> PaperRepository:
    return PaperRepository(session)

def get_paper_service(paper_repository: PaperRepository = Depends(get_paper_repository)) -> PaperService:
    return PaperService(paper_repository)

def get_grobid_parser() -> GrobidParser:
    return GrobidParser(
        httpx_client=_httpx_client,
        grobid_host=settings.GROBID_HOST,
        grobid_port=settings.GROBID_PORT
    )


# parsers
_tagger_llm: Optional[LLMTagger] = None

async def _get_llm_tagger() -> LLMTagger:
    global _tagger_llm

    if _tagger_llm is None:
        instructor_client = instructor.from_provider(
            model=settings.TAGGER_MODEL,
            api_key=settings.TAGGER_API_KEY,
            async_client=True,
            mode=instructor.Mode.XAI_JSON
        )

        _tagger_llm = LLMTagger(instructor_client)

    return _tagger_llm


# Uploading
def get_uploading_orchestrator(
        paper_service: PaperService = Depends(get_paper_service),
        grobid_parser: GrobidParser = Depends(get_grobid_parser),
        llm_tagger: LLMTagger = Depends(_get_llm_tagger),
) -> PaperIngestionService:
    return PaperIngestionService(
        arxiv_provider=_arxiv_provider,
        paper_service=paper_service,
        parser=grobid_parser,
        tagger=llm_tagger,
        batch_size=settings.BATCH_SIZE,
    )


# metadata
# _tags_and_entities_extractor = TagsAndEntitiesExtractor(llm=_grok_llm)

# Downloaders
# _arxiv_downloader = ArxivDownloader()

# Chunkers
# _semantic_base_chunker = SemanticChunker(
#     _embedder,
#     breakpoint_threshold_amount=87.5,
#     sentence_split_regex=r"\n{2,}|#{1,3}\s|(?<![|\s*-*])---(?![-*\s*|])|(?<![|\s*])\n(?![\s*|])|(?<![.])\.(?![\d.])|[?!]",
#     min_chunk_size=150
# )
# _semantic_chunker = SemanticBaseChunker(_semantic_base_chunker)
#
# # Embedders
# _hugging_face_embedder = HuggingFaceEmbedder(_embedder)

# # Repositories
# _chunk_repository = ChunkRepository()
#
# def get_chunk_repository() -> ChunkRepository:
#     return _chunk_repository


# Graph
# _graph = Graph(
#     llm=_grok_llm,
#     reranker=_reranker,
#     logger=_logger,
#     vector_store=_vector_store,
# )

# Services
# _chunks_service = ChunkService(_chunk_repository)
# _rag_service = RAGService(
#     downloader=_arxiv_downloader,
#     parser=_llama_parser,
#     chunker=_semantic_chunker,
#     embedder=_hugging_face_embedder,
#     chunk_service=_chunks_service,
#     graph=_graph
# )


# def get_chunks_service() -> ChunkService:
#     return _chunks_service

# def get_rag_service():
#     return _rag_service