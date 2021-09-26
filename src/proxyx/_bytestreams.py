import httpx
from typing import AsyncIterable, AsyncIterator
import inspect


class AsyncIteratorByteStream(httpx.AsyncByteStream):
    """
    A copy of httpx._content.AsyncIteratorByteStream, which is private.
    """

    def __init__(self, stream: AsyncIterable[bytes]):
        self._stream = stream
        self._is_stream_consumed = False
        self._is_generator = inspect.isasyncgen(stream)

    async def __aiter__(self) -> AsyncIterator[bytes]:
        if self._is_stream_consumed and self._is_generator:
            raise httpx.StreamConsumed()

        self._is_stream_consumed = True
        async for part in self._stream:
            yield part
