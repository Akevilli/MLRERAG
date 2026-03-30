from typing import List, Tuple
from abc import ABC, abstractmethod

from src.shared.schemas import ArxivMetadata, ArxivPaper


class Parser(ABC):
    @abstractmethod

    async def parse(self, unloaded_papers: List[Tuple[ArxivMetadata, bytes]]) -> list[ArxivPaper]:
        pass