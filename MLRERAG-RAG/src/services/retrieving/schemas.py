from typing import List, Optional, Annotated

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from src.shared.schemas import ArxivMetadata, ChunkedSection, Chunk, Table


class RetrievedDocumentMetadata(ArxivMetadata):
    tags: Optional[List[str]] = Field(default=None, description="Paper's tags.")
    is_loaded: bool = Field(description="Whether the document has been loaded.")

    def __str__(self) -> str:
        return f"""# {self.title}
        ---
        arxiv_id: {self.arxiv_id}
        version: {self.version}
        summary: {self.summary}
        source: {self.source_url}
        authors: {" ".join(self.authors)}
        {f"tags: {' '.join(self.tags)}" if self.tags else None}
        ---
        """

class RetrievedChunk(Chunk):
    references: List[RetrievedDocumentMetadata] = Field(default_factory=list, description="Chunk's references.")
    tables: List[Table] = Field(default_factory=list, description="Chunk's tables.")

    def __str__(self) -> str:
        return f"{self.text}\npage: {self.page}"

class RetrievedChunkedSection(ChunkedSection):
    chunks: List[RetrievedChunk] = Field(default_factory=list, description="Paper's chunks.")

    def __str__(self) -> str:
        return (f"{self.number} {self.title} - page: {self.page}\n\n"
                + f"\n".join([str(chunk) for chunk in self.chunks]))

class RetrievedDocumentBase(BaseModel):
    metadata: RetrievedDocumentMetadata = Field(description="Paper's metadata.")

class RetrievedDocument(RetrievedDocumentBase):
    sections: List[RetrievedChunkedSection] = Field(default_factory=list, description="Paper's sections.")
    tables: List[Table] = Field(default_factory=list, description="Paper's tables.")
    references: List[RetrievedDocumentMetadata] = Field(default_factory=list, description="Paper's references.")

    def __str__(self) -> str:
        return f"""{str(self.metadata)}
            {"\n\n".join([str(section) for section in self.sections])}
            Tables:
            {"\n\n".join([str(table) for table in self.tables])}
            References:
            {"\n\n".join([str(reference) for reference in self.references])}
        """

class AgentState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = Field(description="Chat's messages.")
