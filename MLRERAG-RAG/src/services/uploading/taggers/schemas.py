from typing import List

from pydantic import BaseModel, Field

from src.shared.schemas import PaperTag


class PaperTaggingResult(BaseModel):
    """Schema for the result of paper tagging.

    Contains the extracted tags from a paper analysis.
    """

    tags: List[PaperTag] = Field(description="List of hierarchical semantic tags.")