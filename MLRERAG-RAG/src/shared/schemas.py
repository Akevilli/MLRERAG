from typing import List, Sequence
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class PaperUploadDTO(BaseModel):
    """Data transfer object for paper upload requests."""
    id_list: List[str]


class UploadedPaperDTO(BaseModel):
    """Data transfer object for uploaded paper responses."""
    loaded: set[str]
    failed: set[str]
    cited: set[str]


class ArxivMetadata(BaseModel):
    """Metadata model for arXiv paper information."""
    arxiv_id: str = Field(description="arXiv's paper identifier")
    version: str = Field(description="arXiv's paper version")
    title: str = Field(description="Paper title.")
    summary: str = Field(description="Paper summary.")
    source_url: str = Field(description="Paper's source URL.")
    authors: List[str] = Field(description="List of authors.")


class PaperDomain(str, Enum):
    """Enumeration of primary research domains on ArXiv.

    Attributes:
        NLP: Natural Language Processing.
        CV: Computer Vision.
        AUDIO: Audio, Speech, and Music processing.
        RL: Reinforcement Learning.
        GEN: Generative AI and Modeling.
        TIMESERIES: Time-series Analysis and Forecasting.
        TABULAR: Tabular Data and Classical ML.
        RECSYS: Recommender Systems.
        GENERAL: General AI concepts (Optimization, Theory, etc.).
        OTHER: Research areas not covered by specific domains.
    """
    NLP = "nlp"
    CV = "cv"
    AUDIO = "audio"
    RL = "rl"
    GEN = "gen"
    TIMESERIES = "timeseries"
    TABULAR = "tabular"
    RECSYS = "recsys"
    GENERAL = "general"
    OTHER = "other"


class EntityCategory(str, Enum):
    """Functional classification of a technical entity.

    Attributes:
        ARCH: Structural models or specific pre-trained architectures.
        TASK: Specific applications or research objectives.
        METHOD: Mathematical approaches, algorithms, or training techniques.
        DATASET: Reference data collections or benchmarks.
        METRIC: Evaluation standards and performance measures.
    """
    ARCH = "arch"
    TASK = "task"
    METHOD = "method"
    DATASET = "dataset"
    METRIC = "metric"


class PaperTag(BaseModel):
    """Hierarchical semantic tag for document categorization and filtering.

    This model represents a semantic path used for precise metadata filtering
    in vector databases (e.g., Qdrant) and citation enrichment.

    Attributes:
        domain (PaperDomain): The broad technical field.
        category (EntityCategory): The functional role of the entity.
        entity (Entity): The specific technical concept.
    """
    domain: PaperDomain = Field(description="The technical domain of the tag.")
    category: EntityCategory = Field(description="The functional role of the entity.")
    entity: str = Field(description="""The normalized technical term.
                                        Must follow these formatting rules:
                                        - Kebab-case: Replace spaces and underscores with hyphens
                                          (e.g., 'stable-diffusion' instead of 'stable_diffusion').
                                        - Lowercase: Use strictly lowercase characters.
                                        - Singular: Use singular forms (e.g., 'transformer' instead of 'transformers').
                                        - Acronyms: Use standard technical acronyms where applicable
                                          (e.g., 'ner', 'cnn', 'bert').""")

    def __str__(self) -> str:
        """Returns the string representations of the hierarchical tag path.

        Returns:
            str: The string representation of the hierarchical tag path.
        """
        return f"{self.domain.value}/{self.category.value}/{self.entity}"

class Table(BaseModel):
    """Model representing a table extracted from a paper."""
    id: UUID = Field(description="Table id.")
    caption: str = Field(description="Table caption.")
    text: str = Field(description="Table text.")
    description: str = Field(description="Table description.")
    page: str = Field(description="Table page number.")

    def get_full_text(self) -> str:
        """Returns the string representation of the table, with caption and description."""

        return f"{self.caption} - page: {self.page}\n\n{self.text}\n\n{self.description}"

class Reference(BaseModel):
    """Model representing a bibliography reference."""
    arxiv_id: str = Field(description="Id of paper which was referenced.")

class Paragraph(BaseModel):
    """Model representing a paragraph within a paper section."""
    text: str = Field(description="Paper text.")
    page: str = Field(description="Paper page number.")
    tables: List[Table] = Field(description="Table list.")
    references: List[Reference] = Field(description="Reference list.")

    def __str__(self) -> str:
        """Returns the string representation of the paragraph.
        Returns:
            str: The paragraph.
        """
        return self.text

class SectionBase(BaseModel):
    """Model representing a document section without its content."""
    id: UUID = Field(description="Unique identifier of section.")
    number: str = Field(description="Section number.")
    title: str = Field(description="Section title.")
    page: str = Field(description="Section page.")

class Section(SectionBase):
    """Model representing a document section with its content via paragraphs."""
    paragraphs: List[Paragraph] = Field(description="Section paragraphs.")

    def __str__(self) -> str:
        """Returns the string representation of the section.
        Returns:
            str: The string representation of the section.
        """

        return f"{self.number} {self.title}\n\n" + "\n".join([str(paragraph) for paragraph in self.paragraphs])

class ArxivPaperBase(BaseModel):
    """Model representing an arxiv paper without content."""
    references: List[Reference] = Field(description="List of references.")
    metadata: ArxivMetadata = Field(description="Arxiv metadata.")

class ArxivPaper(ArxivPaperBase):
    """Model representing a parsed arXiv paper with structured content."""
    sections: List[Section] = Field(description="List of sections.")
    tables: List[Table] = Field(description="List of tables.")


class TaggedArxivPaper(ArxivPaper):
    """Model representing a parsed arXiv paper with structured content and tags."""
    tags: List[PaperTag] = Field(description="List of paper tags.")

    @field_serializer("tags", when_used="json")
    def serialize_tags(self, tags: List[PaperTag]) -> List[str]:
        return [str(tag) for tag in tags]


class Chunk(BaseModel):
    """Schema representing a paper chunk for the uploading process.

    A chunk is a segment of a paper's content, used for downstream processing and storage.

    Attributes:
        text: The text content of the chunk.
        page: The number of page where the chunk starts.
    """
    id: UUID = Field(description="Chunk ID.")
    text: str = Field(description="Chunk content.")
    position: int = Field(description="Chunk position in section.")
    page: str = Field(description="Chunk page number.")
    tables: List[Table] = Field(description="Chunk tables.")
    references: List[Reference] = Field(description="Chunk references.")

class ChunkedSection(SectionBase):
    """Model representing a paper chunked section."""
    chunks: List[Chunk] = Field(description="List of section's chunks.", default_factory=list)

    def __str__(self) -> str:
        """Returns the string representation of the section."""
        return "\n".join([chunk.content for chunk in self.chunks])

class ChunkedArxivPaper(TaggedArxivPaper):
    """Model representing a parsed arxiv paper with chunked content."""
    sections: List[ChunkedSection] = Field(description="List of chunked sections of paper.", default_factory=list)
    tables: List[Table] = Field(description="List of tables.")

class EmbeddedChunk(Chunk):
    embedding: Sequence[float] = Field(description="Chunk embedding.")

class EmbeddedSection(SectionBase):
    """Model representing a paper embedded section."""
    chunks: List[EmbeddedChunk] = Field(description="List of embedded section's chunks.")

class EmbeddedTable(Table):
    """Model representing a paper embedded table."""
    embedding: Sequence[float] = Field(description="Table embedding.")

class EmbeddedArxivPaper(TaggedArxivPaper):
    """Model representing a parsed arxiv paper with embedded sections and tables."""
    sections: List[EmbeddedSection] = Field(description="List of embedded sections.")
    tables: List[EmbeddedTable] = Field(description="List of embedded tables.")

class MessageType(str, Enum):
    """Enum representing the message type."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class Message(BaseModel):
    """Model representing a message."""
    text: str = Field(description="Message text.")
    type: MessageType = Field(description="Message type.")

class ChatHistory(BaseModel):
    """Model representing a chat history."""
    messages: List[Message] = Field(description="List of messages.")