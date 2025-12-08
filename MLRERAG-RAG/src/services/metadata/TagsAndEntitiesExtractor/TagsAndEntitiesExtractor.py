import yaml

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_xai import ChatXAI

from ..schemas import DocumentTagsAndEntities


class TagsAndEntitiesExtractor:
    def __init__(self, llm: ChatXAI):
        try:
            with open("cache/prompts.yaml", "r") as f:
                self.__prompts = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("Error: prompts/rag_prompts.yaml not found.")

        self.__llm = llm.with_structured_output(DocumentTagsAndEntities, method="json_schema")

    def extract(self, text: str) -> DocumentTagsAndEntities:
        messages = [HumanMessage(text), SystemMessage(self.__prompts["tags_and_entities_extractor_prompt"])]
        output = self.__llm.invoke(messages)
        return output