from typing import Generator, Any

from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal
from .services.downloaders import ArxivDownloader
from .services.parsers import LlamaParser
from .services.chunkers import SemanticBaseChunker
from .services.embedders import HuggingFaceEmbedder
from .core import settings


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