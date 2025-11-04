from .services.downloaders import ArxivDownloader
from .services.parsers import LlamaParser
from .core import settings

# Downloaders
_arxiv_downloader = ArxivDownloader()

def get_arxiv_downloader():
    return _arxiv_downloader


# Parsers
_llama_parser = LlamaParser(settings.LLAMA_PARSER_API_KEY)


def get_llama_parser():
    return _llama_parser