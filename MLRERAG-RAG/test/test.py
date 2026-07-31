import json
import os
import asyncio

import pandas as pd
from tqdm.asyncio import tqdm
from ragas.metrics.collections import Faithfulness, AnswerRelevancy
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from openai import AsyncOpenAI

# Твоя ссылка из Kaggle
NGROK_URL = "https://covenant-auction-sterling.ngrok-free.dev"


async def run_ragas_evaluation(dataset_path: str):
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Файл датасета {dataset_path} не найден.")

    with open(dataset_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Меняем localhost на NGROK_URL и добавляем заголовок обхода варнинга ngrok
    client = AsyncOpenAI(
        base_url=f"{NGROK_URL}/v1",
        api_key="ollama",
        default_headers={"ngrok-skip-browser-warning": "true"},
    )
    ragas_llm = llm_factory(
        model="granite-ragas",
        client=client,
        max_tokens=32768,
        temperature=0.0,
        system_prompt="CRITICAL: Strictly follow shape of response, do NOT add any external field"
    )
    ragas_embedding = embedding_factory(
        "openai",
        model="qwen3-embedding:0.6b",
        client=client
    )

    faithfulness_metric = Faithfulness(llm=ragas_llm)
    response_relevance_metric = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embedding)

    faithfulness_scores = []
    response_relevance_scores = []

    async for item in tqdm(raw_data, desc="Оценка датасета"):
        ctx = item.get("retrieved_contexts", [])
        retrieved_contexts = [ctx] if isinstance(ctx, str) else ctx
        user_input = item.get("user_input", "")
        response = item.get("response", "")

        f_res = await faithfulness_metric.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts
        )
        faithfulness_scores.append(f_res.value)

        r_res = await response_relevance_metric.ascore(
            user_input=user_input,
            response=response,
        )
        response_relevance_scores.append(r_res.value)

    faithfulness_series = pd.Series(name="faithfulness", data=faithfulness_scores).dropna()
    response_relevance_series = pd.Series(name="response relevance", data=response_relevance_scores).dropna()

    print("\n" + "=" * 50 + "\n")
    print(faithfulness_series.describe())
    print("\n" + "=" * 50 + "\n")
    print(response_relevance_series.describe())


if __name__ == "__main__":
    asyncio.run(run_ragas_evaluation(dataset_path="./test/data/dataset.json"))