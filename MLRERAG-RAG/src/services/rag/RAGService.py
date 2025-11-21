from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from src.api.schemas import UploadSchema, UploadResponseSchema, QuerySchema, QueryResponseSchema
from src.services import (
    Downloader,
    Parser,
    Chunker,
    Embedder,
    ChunkService
)
from src.services.graph import Graph, State


class RAGService:
    def __init__(
            self,
            downloader: Downloader,
            parser: Parser,
            chunker: Chunker,
            embedder: Embedder,
            chunk_service: ChunkService,
            graph: Graph,
    ):
        self.__downloader = downloader
        self.__parser = parser
        self.__chunker = chunker
        self.__embedder = embedder
        self.__chunk_service = chunk_service
        self.__graph = graph

    def upload(self, upload_data: UploadSchema, session: Session) -> UploadResponseSchema:
        documents_info = self.__downloader.download(upload_data)
        documents = self.__parser.parse(documents_info)
        chunks = self.__chunker.chunk(documents)
        embedding = self.__embedder.embed_documents(chunks)

        self.__chunk_service.create(embedding, session)

        return UploadResponseSchema(saved_documents=upload_data.id_list)


    def generate_answer(self, query: QuerySchema) -> QueryResponseSchema:
        input_state: State = {
            "messages": [HumanMessage(message.content) if message.is_users else AIMessage(message.content) for message in query.messages],
            "answer": "",
            "documents": ""
        }

        response = self.__graph.invoke(input_state)
        return QueryResponseSchema(
            answer=response["answer"],
            documents=response["documents"]
        )