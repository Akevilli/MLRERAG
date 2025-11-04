import nest_asyncio
nest_asyncio.apply()

from .base_parser import Parser
from llama_cloud_services import LlamaParse
from llama_index.core.schema import Document



class LlamaParser(Parser):
    def __init__(self, api_key: str, num_workers: int = 1, verbose: bool = False, language: str = "en"):
        self.api_key = api_key
        self.num_workers = num_workers
        self.verbose = verbose
        self.language = language

        self.parser = LlamaParse(
            api_key=api_key,
            num_workers=num_workers,
            verbose=verbose,
            language=language,
        )

    def parse(self, paper: list[str]) -> list[Document]:
        results = self.parser.parse(paper)
        documents = [result.get_markdown_documents()[0] for result in results]

        return documents
