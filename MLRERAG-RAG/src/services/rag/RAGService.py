from sqlalchemy.orm import Session
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage, AIMessage

from src.api.schemas import UploadSchema, UploadResponseSchema, QuerySchema, QueryResponseSchema
from src.services import (
    Downloader,
    Parser,
    Chunker,
    Embedder,
    DocumentService,
    ChunkService,
)
from src.core.graph import State


class RAGService:
    def __init__(
            self,
            downloader: Downloader,
            parser: Parser,
            chunker: Chunker,
            embedder: Embedder,
            document_service: DocumentService,
            chunk_service: ChunkService,
            graph: CompiledStateGraph,
    ):
        self.__downloader = downloader
        self.__parser = parser
        self.__chunker = chunker
        self.__embedder = embedder
        self.__document_service = document_service
        self.__chunk_service = chunk_service
        self.__graph = graph

    def upload(self, upload_data: UploadSchema, session: Session) -> UploadResponseSchema:
        corrected_upload_data = UploadSchema(
            id_list=self.__document_service.get_unstored_documents(upload_data.id_list, session)
        )

        if len(corrected_upload_data.id_list) == 0:
            return UploadResponseSchema(saved_documents=[])

        documents_info = self.__downloader.download(corrected_upload_data)
        documents = self.__parser.parse(documents_info)
        self.__document_service.create(documents, session)
        chunks = self.__chunker.chunk(documents)
        embedding = self.__embedder.embed_documents(chunks)

        self.__chunk_service.create(embedding, session)

        return UploadResponseSchema(saved_documents=corrected_upload_data.id_list)


    def generate_answer(self, query: QuerySchema) -> QueryResponseSchema:
        input_state = State(
            answer="",
            messages=[HumanMessage(content=message.content) if message.is_users else AIMessage(message.content) for message in query.messages],
            documents="",
        )

        response = self.__graph.invoke(input_state)
        return QueryResponseSchema(
            answer=response["answer"],
            documents=response["documents"]
        )