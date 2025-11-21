import yake


class YAKE:
    def __init__(
        self,
        language: str = "en",
        max_ngram_size: int = 3,
        deduplication_threshold: float = 0.9,
        deduplication_algo: str = 'seqm',
        window_size: int = 1,
        top: int = 5,
    ):
        self.__keyword_extractor = yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            dedupFunc=deduplication_algo,
            window_size=window_size,
            top=top
        )

    def extract(self, text: str) -> list[str]:
        keywords = self.__keyword_extractor.extract_keywords(text)
        keywords = [keyword for keyword, _ in keywords]
        return keywords