from typing import AsyncGenerator, Optional

import arxiv
import httpx
import instructor
from ollama import AsyncClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_xai import ChatXAI

from sqlalchemy.exc import SQLAlchemyError

from src.shared import SessionLocal, OllamQwenEmbedder, QdrantRepository, qdrant_client
from .services import *
from .core import settings


# Clients
_arxiv_client = arxiv.Client()
_httpx_client = httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"})
_ollama_client = AsyncClient(
    host=f"{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"
)


# Qdrant
_qdrant_repository = QdrantRepository(
    client=qdrant_client,
    collection_name=settings.VECTOR_DB_COLLECTION
)


# arXiv
_arxiv_provider = ArxivProvider(arxiv_client=_arxiv_client, httpx_client=_httpx_client)


_grok_llm = ChatXAI(
    api_key=settings.GROK_API_KEY,
    model=settings.GROK_MODEL
)

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


# Uploading
def get_uploading_orchestrator(
        paper_service: PaperService = Depends(get_paper_service),
        grobid_parser: GrobidParser = Depends(get_grobid_parser),
        llm_tagger: LLMTagger = Depends(_get_llm_tagger),
        section_bound_chunker: SectionBoundChunker = Depends(get_section_bound_chunker),
) -> PaperIngestionService:
    return PaperIngestionService(
        arxiv_provider=_arxiv_provider,
        paper_service=paper_service,
        parser=grobid_parser,
        tagger=llm_tagger,
        chunker=section_bound_chunker,
        embedder=_ollama_embedder,
        qdrant_repository=_qdrant_repository,
        batch_size=settings.BATCH_SIZE,
    )
