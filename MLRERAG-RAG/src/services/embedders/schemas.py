from src.services.chunkers import Chunk


class ChunkWithEmbedding(Chunk):
    embedding: list[float]