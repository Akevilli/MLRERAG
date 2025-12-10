from typing import List, Literal

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    summary: str
    source_url: str
    published_at: str
    authors: List[str]
    domains: List[Literal["nlp", "cv", "ap", "rl", "tabular", "multimodal", "ts", "bio", "other"]] = []
    tasks: List[Literal[
        "text classification", "token classification", "named entity recognition", "Youtubeing",
        "fill mask", "summarization", "translation", "text generation",
        "text to text generation", "zero-shot classification", "conversational",
        "sentence similarity", "table question answering", "feature extraction",
        "text ranking", "image classification", "image segmentation",
        "object detection", "depth estimation", "image to image", "text to image",
        "image to text", "video classification", "keypoint detection",
        "zero-shot image classification", "zero-shot object detection",
        "mask generation", "unconditional image generation", "image feature extraction",
        "background removal", "video to video", "text to video",
        "audio classification", "automatic speech recognition", "text to speech",
        "audio to audio", "voice activity detection", "zero-shot audio classification",
        "visual question answering", "document question answering",
        "image text to text", "audio text to text", "visual document retrieval",
        "text to 3d", "image to 3d", "tabular classification",
        "tabular regression", "time series forecasting", "other"
    ]] = []
    entities: List[str] = []


class Document(BaseModel):
    text: str
    page: int
    document_metadata: DocumentMetadata


class ChunkMetadata(DocumentMetadata):
    page: int


class Chunk(BaseModel):
    text: str
    chunk_metadata: ChunkMetadata


class ChunkWithEmbedding(Chunk):
    embedding: List[float]