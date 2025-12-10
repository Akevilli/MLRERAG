import nest_asyncio

from llama_cloud_services import LlamaParse

from ..BaseParser.BaseParser import Parser
from src.services.metadata import TagsAndEntitiesExtractor
from src.shared.schemas import DocumentMetadata, Document


class LlamaParser(Parser):
    def __init__(
        self,
        parser: LlamaParse,
        metadata_extractor: TagsAndEntitiesExtractor
    ):
        self.__parser = parser
        self.metadata_extractor = metadata_extractor

    def parse(self, documents_info: list[DocumentMetadata]) -> list[Document]:
        paths = [f"./papers/{document.document_id}.pdf" for document in documents_info]
        nest_asyncio.apply()
        results = self.__parser.parse(paths)

        documents = []

        for document_index, document in enumerate(results):
            document_info = documents_info[document_index]

            text = "\n\n".join([
                document_info.title,
                document_info.summary,
                document.get_markdown_documents()[0].text
            ])

            tags_and_entities = self.metadata_extractor.extract(text)
            for page in document.pages:
                documents.append(
                    Document(
                        text=page.md,
                        page=page.page,
                        document_metadata=DocumentMetadata(
                            document_id=document_info.document_id,
                            title=document_info.title,
                            summary=document_info.summary,
                            source_url=document_info.source_url,
                            published_at=document_info.published_at,
                            authors=document_info.authors,
                            **tags_and_entities.model_dump()
                        )
                    )
                )

        return documents