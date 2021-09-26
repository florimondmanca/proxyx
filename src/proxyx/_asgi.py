from typing import List, Optional, Tuple

import httpx
from starlette.requests import Request as ASGIRequest
from starlette.types import Receive, Scope, Send


class ProxyApp:
    _http: httpx.AsyncBaseTransport

    def __init__(self, hostname: str, root_path: str = ""):
        self._hostname = hostname
        self._root_path = root_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
        else:
            assert scope["type"] == "http"
            await self._http_request(scope, receive, send)

    async def _lifespan(self, scope: Scope, receive: Receive, send: Send) -> None:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                self._http = httpx.AsyncHTTPTransport()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await self._http.aclose()
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _http_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        method, url, headers, stream = self._get_request(scope, receive)

        status_code, headers, stream, ext = await self._http.handle_async_request(
            method=method,
            url=url,
            headers=headers,
            stream=stream,
            extensions={},
        )

        assert ext["http_version"] == b"HTTP/1.1"

        await send(
            {"type": "http.response.start", "status": status_code, "headers": headers}
        )

        try:
            async for chunk in stream:
                await send(
                    {"type": "http.response.body", "body": chunk, "more_body": True}
                )
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        finally:
            await stream.aclose()

    def _get_request(
        self, scope: Scope, receive: Receive
    ) -> Tuple[
        bytes,
        Tuple[bytes, bytes, Optional[int], bytes],
        List[Tuple[bytes, bytes]],
        httpx.AsyncByteStream,
    ]:
        asgi_request = ASGIRequest(scope, receive=receive)

        method = asgi_request.method.encode("utf-8")

        url = httpx.URL(
            scheme="https",  # Only allow proxying to HTTPS services.
            host=self._hostname,  # Swap hostname.
            path=self._root_path + asgi_request.url.path,  # Inject root path.
            query=asgi_request.url.query.encode("utf-8"),
        )

        headers = asgi_request.headers.mutablecopy()
        headers["host"] = self._hostname  # Swap hostname.

        # Build a full HTTPX request to get a proper HTTPX stream object, using
        # the HTTPX public API only.
        # (We'd actually only want `httpx._content.encode_content()`,
        # or `httpx._content.AsyncIterableStream`.)
        httpx_request = httpx.Request(
            method=method,
            url=url,
            content=asgi_request.stream(),
        )
        stream = httpx_request.stream
        assert isinstance(stream, httpx.AsyncByteStream)

        return method, url.raw, headers.raw, stream
