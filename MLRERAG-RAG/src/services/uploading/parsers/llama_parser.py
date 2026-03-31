import nest_asyncio

from llama_cloud_services import LlamaParse

from src.services.uploading.parsers.base_parser import Parser
from src.services.metadata import TagsAndEntitiesExtractor
from src.shared.schemas import DocumentMetadata, Document


class LlamaParser(Parser):
    """Parser implementation using LlamaParse to extract structured content from PDFs.

    Uses LlamaParse for PDF parsing and optionally extracts tags and entities
    using a metadata extractor.

    Attributes:
        __parser: The LlamaParse instance for PDF processing.
        metadata_extractor: Optional extractor for tags and entities.
    """

    def __init__(
        self,
        parser: LlamaParse,
        metadata_extractor: TagsAndEntitiesExtractor
    ):
        """Initializes the LlamaParser with required dependencies.

        Args:
            parser: A LlamaParse instance configured for PDF parsing.
            metadata_extractor: Extractor for additional metadata like tags and entities.
        """
        self.__parser = parser
        self.metadata_extractor = metadata_extractor

    def parse(self, documents_info: list[DocumentMetadata]) -> list[Document]:
        """Parses PDF documents into structured Document objects.

        Args:
            documents_info: List of DocumentMetadata containing PDF paths and metadata.

        Returns:
            List of Document objects with extracted text and metadata.
        """
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