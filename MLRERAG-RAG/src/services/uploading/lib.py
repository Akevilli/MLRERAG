from typing import AsyncGenerator, Tuple, List


async def get_batch(
        download_generator: AsyncGenerator[Tuple[str, bytes], None],
        batch_size: int
) -> AsyncGenerator[List[Tuple[str, bytes]], None]:
    """Batches items from an async generator into fixed-size lists.

    Collects items from the download generator until the batch reaches
    the specified size, then yields the batch. Remaining items are
    yielded as a final partial batch.

    Args:
        download_generator: An async generator yielding (id, bytes) tuples.
        batch_size: The maximum number of items per batch.

    Yields:
        Lists of (id, bytes) tuples with length up to batch_size.
    """
    batch = []

    async for item in download_generator:
        batch.append(item)
        if len(batch) < batch_size:
            continue

        yield batch
        batch.clear()

    if batch:
        yield batch