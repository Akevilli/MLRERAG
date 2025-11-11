from typing import Generator, Any
from logging import Logger

from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal
from .repositories import *
from .services import *
from .core import settings, _logger, graph


# Logger
def get_logger() -> Logger:
    return _logger


# Models
_embedder = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDER_NAME,
    model_kwargs={'device': settings.DEVICE},
    encode_kwargs={'normalize_embeddings': True}
)


# DB
_session = SessionLocal()

def get_session() -> Generator[Session, Any, None]:
    try:
        yield _session
        _session.commit()

    except SQLAlchemyError:
        _session.rollback()
        raise

    finally:
        _session.close()


# Downloaders
_arxiv_downloader = ArxivDownloader()

def get_arxiv_downloader():
    return _arxiv_downloader


# Parsers
_llama_parser = LlamaParser(settings.LLAMA_PARSER_API_KEY)

def get_llama_parser():
    return _llama_parser


# Chunkers
_semantic_chunker = SemanticBaseChunker(_embedder)

def get_semantic_chunker():
    return _semantic_chunker


# Embedders
_hugging_face_embedder = HuggingFaceEmbedder(_embedder)

def get_huggingface_embedder():
    return _hugging_face_embedder


# Repositories
_document_repository = DocumentRepository()
_chunk_repository = ChunkRepository()

def get_document_repository() -> DocumentRepository:
    return _document_repository

def get_chunk_repository() -> ChunkRepository:
    return _chunk_repository


# Services
_document_service = DocumentService(_document_repository)
_chunks_service = ChunkService(_chunk_repository)
_rag_service = RAGService(
    downloader=_arxiv_downloader,
    parser=_llama_parser,
    chunker=_semantic_chunker,
    embedder=_hugging_face_embedder,
    document_service=_document_service,
    chunk_service=_chunks_service,
    graph=graph
)

def get_document_service() -> DocumentService:
    return _document_service

def get_chunks_service() -> ChunkService:
    return _chunks_service

def get_rag_service():
    return _rag_service