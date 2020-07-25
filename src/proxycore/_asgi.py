from typing import Optional, Tuple

import httpcore
from starlette.requests import Request
from starlette.types import Receive, Scope, Send


class ProxyApp:
    http: httpcore.AsyncHTTPTransport

    def __init__(self, hostname: str, root_path: str = ""):
        self.hostname = hostname
        self.root_path = root_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
        else:
            assert scope["type"] == "http"
            await self._request(scope, receive, send)

    async def _lifespan(self, scope: Scope, receive: Receive, send: Send) -> None:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                self.http = httpcore.AsyncConnectionPool()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await self.http.aclose()
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _request(self, scope: Scope, receive: Receive, send: Send) -> None:
        _, status_code, _, headers, stream = await self.http.request(
            method=self._get_method(scope),
            url=self._get_url(scope),
            headers=self._get_headers(scope),
            stream=self._get_stream(scope, receive),
        )

        is_redirect = 300 <= status_code < 400
        assert not is_redirect, f"{status_code}: Redirects are not supported yet"

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

    def _get_method(self, scope: Scope) -> bytes:
        return scope["method"].encode("utf-8")

    def _get_url(self, scope: Scope) -> Tuple[bytes, bytes, int, bytes]:
        host = self.hostname.encode("utf-8")

        full_path = (self.root_path + scope["path"]).encode("utf-8")
        if scope["query_string"]:
            full_path += b"?%s" % scope["query_string"]

        return (b"https", host, 443, full_path)

    def _get_headers(self, scope: Scope) -> list:
        headers = [(key, value) for key, value in scope["headers"] if key != b"host"]
        headers.append((b"host", self.hostname.encode("utf-8")))
        return headers

    def _get_stream(
        self, scope: Scope, receive: Receive
    ) -> Optional[httpcore.AsyncByteStream]:
        request = Request(scope, receive=receive)
        if (
            "content-length" in request.headers
            or "transfer-encoding" in request.headers
        ):
            return httpcore.AsyncByteStream(request.stream())
        return None
