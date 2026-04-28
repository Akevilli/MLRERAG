from typing import AsyncGenerator, Optional

import arxiv
import neo4j
import httpx
import instructor
from ollama import AsyncClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_xai import ChatXAI

from sqlalchemy.exc import SQLAlchemyError

from src.shared import (
    SessionLocal,
    OllamQwenEmbedder,
    QdrantRepository,
    Neo4jRepository,
    qdrant_client,
    neo4j_client
)
from .services import *
from .core import settings

# Clients
_arxiv_client = arxiv.Client()
_httpx_client = httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"})
_ollama_client = AsyncClient(
    host=f"{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"
)

# LLM
chat_xai = ChatXAI(
    model=settings.GROK_MODEL,
    api_key=settings.GROK_API_KEY,
)

# arXiv
_arxiv_provider = ArxivProvider(arxiv_client=_arxiv_client, httpx_client=_httpx_client)


# DBs
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    session = SessionLocal()
    try:
        yield session
        await session.commit()

    except SQLAlchemyError:
        await session.rollback()
        raise

    finally:
        await session.close()

async def get_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    async with neo4j_client.session(database=settings.GRAPH_DB_DATABASE) as session:
        yield session
        await session.close()


# Qdrant
_qdrant_repository = QdrantRepository(
    client=qdrant_client,
    collection_name=settings.VECTOR_DB_COLLECTION
)

async def get_neo4j_repository(
        session: neo4j.AsyncSession = Depends(get_neo4j_session)
):
    return Neo4jRepository(session=session)

# papers
def get_paper_repository(session: AsyncSession = Depends(get_postgres_session)) -> PaperRepository:
    return PaperRepository(session)

def get_paper_service(paper_repository: PaperRepository = Depends(get_paper_repository)) -> PaperService:
    return PaperService(paper_repository)

# parsers
def get_grobid_parser() -> GrobidParser:
    return GrobidParser(
        httpx_client=_httpx_client,
        grobid_host=settings.GROBID_HOST,
        grobid_port=settings.GROBID_PORT
    )

# tagger
_tagger_llm: Optional[LLMTagger] = None

async def get_llm_tagger() -> LLMTagger:
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

# chunker
def get_section_bound_chunker() -> SectionBoundChunker:
    return SectionBoundChunker(
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.OVERLAP
    )

# embedder
_ollama_embedder = OllamQwenEmbedder(
    ollama_client=_ollama_client,
    model=settings.EMBEDDER_MODEL,
    batch_size=settings.EMBEDDER_BATCH_SIZE,
    embedding_dim=settings.EMBEDDING_DIM,
)


# uploading
def get_uploading_orchestrator(
        paper_service: PaperService = Depends(get_paper_service),
        grobid_parser: GrobidParser = Depends(get_grobid_parser),
        llm_tagger: LLMTagger = Depends(get_llm_tagger),
        section_bound_chunker: SectionBoundChunker = Depends(get_section_bound_chunker),
        neo4j_repository: Neo4jRepository = Depends(get_neo4j_repository),
) -> PaperIngestionService:
    return PaperIngestionService(
        arxiv_provider=_arxiv_provider,
        paper_service=paper_service,
        parser=grobid_parser,
        tagger=llm_tagger,
        chunker=section_bound_chunker,
        embedder=_ollama_embedder,
        qdrant_repository=_qdrant_repository,
        neo4j_repository=neo4j_repository,
        batch_size=settings.BATCH_SIZE,
    )

# search engine
async def _get_search_engine(
        neo4j_repository: Neo4jRepository = Depends(get_neo4j_repository),
):
    return SearchEngine(
        qdrant_repository=_qdrant_repository,
        neo4j_repository=neo4j_repository,
    )

# retrieving
def get_retrieving_orchestrator(
        search_engine: SearchEngine = Depends(_get_search_engine),
):
    return RetrievingService(
        embedder=_ollama_embedder,
        search_engine=search_engine,
        llm=chat_xai
    )