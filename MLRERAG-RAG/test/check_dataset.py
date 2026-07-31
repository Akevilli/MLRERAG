import sys
import json
import asyncio
from src.dependencies import _qdrant_repository, _ollama_embedder


async def check_dataset(path: str):
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    for question in questions:
        embedding = await _ollama_embedder.embed_query([question])
        results = await _qdrant_repository.query(embedding, tags=[])

        assert len(results) != 0
    
    print("Succes!")


asyncio.run(check_dataset(sys.argv[1]))