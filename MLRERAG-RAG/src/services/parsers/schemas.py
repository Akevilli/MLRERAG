from src.services.chunks import DocumentMetadata


class Document(DocumentMetadata):
    text: str
    page: int
    keywords: list[str]