from pydantic import BaseModel, Field
from typing import List, Literal


class DocumentTagsAndEntities(BaseModel):
    domains: List[Literal[
        "nlp", "cv", "ap", "rl", "tabular", "multimodal", "ts", "bio", "other"
    ]] = Field(
        ...,
        description="A list of mandatory document-level tags defining the primary overarching field of study (Domain) "
                    "of the document. Values must be selected from the controlled DOMAIN LIST."
    )

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
    ]] = Field(
        ...,
        description="A list of mandatory document-level tags defining the primary applications or functions (Tasks) "
                    "described by the document. Values must be selected from the controlled TASK LIST."
    )

    entities: List[str] = Field(
        ...,
        description="A list of normalized, lowercase strings representing the main entities "
                    "(e.g., proper nouns, key concepts) mentioned within the document."
    )