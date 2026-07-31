import asyncio
import json

from src.dependencies import get_retrieving_orchestrator
from src.shared.schemas import Message, ChatHistory, MessageType

from src.shared import (
    qdrant_client,
    neo4j_client,
    QdrantRepository,
    Neo4jRepository,
)
from src.core import settings
from src.services.retrieving.orchestrator import SearchEngine


async def generate_dataset(question_path: str, dataset_path: str):
    with open(question_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    responses = []

    async with neo4j_client.session(database=settings.GRAPH_DB_DATABASE) as session:

        neo4j_repo = Neo4jRepository(session=session)
        qdrant_repo = QdrantRepository(
            client=qdrant_client,
            collection_name=settings.VECTOR_DB_COLLECTION
        )

        real_search_engine = SearchEngine(
            qdrant_repository=qdrant_repo,
            neo4j_repository=neo4j_repo
        )

        rag = get_retrieving_orchestrator(search_engine=real_search_engine)

        for i, question in enumerate(questions):
            current_q = "You have to use rag tool and retrieve at least one document: " + question

            history = await rag.generate_answer(
                ChatHistory(
                    messages=[Message(text=current_q, type=MessageType.USER)]
                )
            )

            response = history.messages[-1]
            tool_messages = [
                message.text for message in history.messages
                if message.type == MessageType.TOOL
            ]

            responses.append(
                {
                    "user_input": current_q,
                    "response": response.text,
                    "retrieved_contexts": tool_messages
                }
            )

            with open(dataset_path, "w", encoding="utf-8") as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(
        generate_dataset(
            question_path="./test/data/questions.json",
            dataset_path="./test/data/dataset.json"
        )
    )