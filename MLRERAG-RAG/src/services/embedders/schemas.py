from src.services.chunkers import Chunk


class ChunkWithEmbeddings(Chunk):
    embedding: list[float]