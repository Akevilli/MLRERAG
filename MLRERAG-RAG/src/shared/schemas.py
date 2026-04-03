from typing import List, Sequence
from enum import Enum

from pydantic import BaseModel, Field


class PaperUploadDTO(BaseModel):
    """Data transfer object for paper upload requests."""
    id_list: List[str]


class UploadedPaperDTO(BaseModel):
    """Data transfer object for uploaded paper responses."""
    id_list: List[str]


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


class Paragraph(BaseModel):
    """Model representing a paragraph within a paper section."""
    text: str = Field(description="Paper text.")
    page: str = Field(description="Paper page number.")

    def __str__(self) -> str:
        """Returns the string representation of the paragraph.
        Returns:
            str: The paragraph.
        """
        return self.text

class Section(BaseModel):
    """Model representing a document section with its content."""
    number: str = Field(description="Section number.")
    title: str = Field(description="Section title.")
    page: str = Field(description="Section page.")
    paragraphs: List[Paragraph] = Field(description="Section paragraphs.")

    def __str__(self) -> str:
        """Returns the string representation of the section.
        Returns:
            str: The string representation of the section.
        """

        return f"{self.number} {self.title}\n\n" + "\n".join([str(paragraph) for paragraph in self.paragraphs])

class Table(BaseModel):
    """Model representing a table extracted from a paper."""
    caption: str = Field(description="Table caption.")
    text: str = Field(description="Table text.")
    description: str = Field(description="Table description.")
    page: str = Field(description="Table page number.")

class Reference(BaseModel):
    """Model representing a bibliography reference."""
    link: str = Field(description="Reference link.")

class ArxivPaper(BaseModel):
    """Model representing a parsed arXiv paper with structured content."""
    sections: List[Section] = Field(description="List of sections.")
    tables: List[Table] = Field(description="List of tables.")
    references: List[Reference] = Field(description="List of references.")
    metadata: ArxivMetadata = Field(description="Arxiv metadata.")


class ArxivPaperWithTags(ArxivPaper):
    """Model representing a parsed arXiv paper with structured content and tags."""
    tags: List[PaperTag] = Field(description="List of paper tags.")


class ChunkMetadata(ArxivMetadata):
    """Metadata associated with a paper chunk.

    Extends ArxivMetadata with chunk-specific information including
    tags, page location, and section name.

    Attributes:
        tags: List of paper tags associated with the chunk.
        page: Page number where the chunk starts.
        section_name: Name of the section containing the chunk.
    """

    tags: List[PaperTag] = Field(description="List of paper tags.")
    page: str = Field(description="Page where chunk starts.")
    section_name: str = Field(description="Section where chunk locates.")

class Chunk(BaseModel):
    """Schema representing a paper chunk for the uploading process.

    A chunk is a segment of a paper's content with associated metadata,
    used for downstream processing and storage.

    Attributes:
        content: The text content of the chunk.
        metadata: Metadata describing the chunk's source and location.
    """

    content: str = Field(description="Chunk content.")
    metadata: ChunkMetadata = Field(description="Chunk metadata.")

class ChunkWithEmbedding(Chunk):
    embedding: Sequence[float] = Field(description="Chunk embedding.")