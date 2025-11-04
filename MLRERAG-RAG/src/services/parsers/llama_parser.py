import nest_asyncio
nest_asyncio.apply()

from .base_parser import Parser
from llama_cloud_services import LlamaParse



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

    def parse(self, paper: list[str]):
        results = self.parser.parse(paper)
        results = [result.get_markdown_documents()[0].text.replace("\n", "") for result in results]

        return results
