import asyncio
from typing import List

import yaml
from instructor import AsyncInstructor

from .base_tagger import Tagger
from .schemas import PaperTaggingResult
from .lib import construct_user_prompt
from src.shared.schemas import (
    ArxivPaper,
    ArxivPaperWithTags,
)


class LLMTagger(Tagger):
    """Tagger implementation that uses an LLM to extract tags from papers.

    This tagger uses an instructor-wrapped LLM client to analyze paper metadata
    and generate relevant tags based on the paper's title and abstract.

    Attributes:
        _instructor_client: The instructor client used for LLM interactions.
        _system_prompt: The system prompt loaded from the prompts cache.
    """

    def __init__(
            self,
            instructor_client: AsyncInstructor,
    ):
        """Initializes the LLMTagger with an instructor client.

        Args:
            instructor_client: An AsyncInstructor instance configured with an LLM
                backend for structured output generation.
        """
        self._instructor_client = instructor_client

        with open("cache/prompts.yaml") as file:
            self._system_prompt = yaml.safe_load(file)["tagger_system_prompt"]

    async def _tag_single(self, paper: ArxivPaper) -> ArxivPaperWithTags:
        """Tags a single paper using the LLM.

        Args:
            paper: An ArxivPaper instance containing the paper metadata to tag.

        Returns:
            An ArxivPaperWithTags instance containing the original paper data
            along with the extracted tags.
        """
        response = await self._instructor_client.create(
            response_model=PaperTaggingResult,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": construct_user_prompt(paper)}
            ]
        )

        return ArxivPaperWithTags(**paper.model_dump(), tags=response.tags)

    async def tag(self, papers: List[ArxivPaper]) -> List[ArxivPaperWithTags]:
        """Tags multiple papers concurrently using the LLM.

        Args:
            papers: A list of ArxivPaper instances to tag.

        Returns:
            A list of ArxivPaperWithTags instances, one for each input paper,
            preserving the original order.
        """
        tasks = [self._tag_single(paper) for paper in papers]
        return await asyncio.gather(*tasks)
