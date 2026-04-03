from typing import Iterable, AsyncIterable, AsyncIterator, List, Union, TypeVar


T = TypeVar('T')


async def _to_async_iterator(iterable: Union[AsyncIterable[T], Iterable[T]]) -> AsyncIterator[T]:
    if isinstance(iterable, AsyncIterable):
        async for item in iterable:
            yield item
    else:
        for item in iterable:
            yield item


async def get_batch(
        iterable: Union[Iterable[T], AsyncIterable[T]],
        batch_size: int
) -> AsyncIterator[List[T]]:
    batch = []

    async for item in _to_async_iterator(iterable):
        batch.append(item)
        if len(batch) < batch_size:
            continue

        yield batch
        batch = []

    if batch:
        yield batch