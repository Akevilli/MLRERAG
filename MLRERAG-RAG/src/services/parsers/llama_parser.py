import nest_asyncio
nest_asyncio.apply()

from llama_cloud_services import LlamaParse

from .base_parser import Parser
from .schemas import Document
from src.services.downloaders import DocumentInfo


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

    def parse(self, documents_info: list[DocumentInfo]) -> list[Document]:
        paths = [f"./papers/{document.id}.pdf" for document in documents_info]
        results = self.parser.parse(paths)

        documents = []

        for index, result in enumerate(results):
            document = Document(
                **documents_info[index].model_dump(),
                text=result.get_markdown_documents()[0].text
            )

            documents.append(document)

        return documents
