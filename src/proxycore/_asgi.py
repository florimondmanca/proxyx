from typing import Optional

import httpcore
from starlette.requests import Request


class ProxyApp:
    http: httpcore.AsyncHTTPTransport

    def __init__(self, hostname: str, root_path: str = ""):
        self.hostname = hostname
        self.root_path = root_path

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
        else:
            assert scope["type"] == "http"
            await self._request(scope, receive, send)

    async def _lifespan(self, scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                self.http = httpcore.AsyncConnectionPool()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await self.http.aclose()
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _request(self, scope, receive, send):
        _, status_code, _, headers, stream = await self.http.request(
            method=self._get_method(scope),
            url=self._get_url(scope),
            headers=self._get_headers(scope),
            stream=self._get_stream(scope, receive),
        )

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

    def _get_method(self, scope: dict) -> bytes:
        return scope["method"].encode("utf-8")

    def _get_url(self, scope: dict) -> tuple:
        host = self.hostname.encode("utf-8")

        full_path = (self.root_path + scope["path"]).encode("utf-8")
        if scope["query_string"]:
            full_path += b"?%s" % scope["query_string"]

        return (b"https", host, 443, full_path)

    def _get_headers(self, scope: dict) -> list:
        headers = [(key, value) for key, value in scope["headers"] if key != b"host"]
        headers.append((b"host", self.hostname.encode("utf-8")))
        return headers

    def _get_stream(self, scope, receive) -> Optional[httpcore.AsyncByteStream]:
        request = Request(scope, receive=receive)
        if (
            "content-length" in request.headers
            or "transfer-encoding" in request.headers
        ):
            return httpcore.AsyncByteStream(request.stream())
        return None
