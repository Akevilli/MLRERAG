import nest_asyncio

from llama_cloud_services import LlamaParse

from ..BaseParser.BaseParser import Parser
from ..schemas import Document
from src.services.chunks import DocumentMetadata
from src.services.metadata import YAKE


class LlamaParser(Parser):
    def __init__(
        self,
        parser: LlamaParse,
        keywords_extractor: YAKE
    ):
        self.__parser = parser
        self.__keywords_extractor = keywords_extractor

    def parse(self, documents_info: list[DocumentMetadata]) -> list[Document]:
        paths = [f"./papers/{document.document_id}.pdf" for document in documents_info]
        nest_asyncio.apply()
        results = self.__parser.parse(paths)

        documents = []

        for document_index, document in enumerate(results):
            text = documents_info[document_index].summary + " " + document.get_text_documents()[0].text
            keywords = self.__keywords_extractor.extract(text)
            keywords = [keyword.lower() for keyword in keywords]
            for page in document.pages:
                documents.append(
                    Document(
                        text=page.md,
                        page=page.page,
                        keywords=keywords,
                        **documents_info[document_index].model_dump()
                    )
                )

        return documents