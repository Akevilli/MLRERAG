import nest_asyncio
nest_asyncio.apply()

from llama_cloud_services import LlamaParse

from src.services.downloaders import DocumentInfo
from ..BaseParser.BaseParser import Parser
from ..schemas import Document


class LlamaParser(Parser):
    def __init__(self, parser: LlamaParse):
        self.__parser = parser

    def parse(self, documents_info: list[DocumentInfo]) -> list[Document]:
        paths = [f"./papers/{document.id}.pdf" for document in documents_info]
        results = self.__parser.parse(paths)

        documents = []

        for index, result in enumerate(results):
            document = Document(
                **documents_info[index].model_dump(),
                text=result.get_markdown_documents()[0].text
            )

            documents.append(document)

        return documents
