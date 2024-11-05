import json
from typing import Any, Mapping, AsyncGenerator
from urllib.parse import parse_qsl

from vines.http.utils import parse_cookie
from vines.core.types import Scope, Receive, Message
from vines.core.exceptions import RequestAborted


class HttpHeaders(Mapping[str, str]):
    """A dictionary-like class to manage HTTP headers with case-insensitive keys."""

    def __init__(self, headers: list[tuple[bytes, bytes]]) -> None:
        self._headers: dict[str, str] = {
            header.decode('latin1').lower(): value.decode('latin1')
            for header, value in headers
        }

    def __getitem__(self, key: str) -> str:
        return self._headers[key.lower()]

    def __iter__(self) -> iter:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def __repr__(self) -> str:
        return str(self._headers)

    def has(self, key: str) -> bool:
        return key.lower() in self._headers


class HttpRequest:
    """Represents an HTTP request, parsing and providing access to its components."""

    def __init__(self, scope: Scope, receive: Receive) -> None:
        self.scope: Scope = scope
        self.receive: Receive = receive
        self._query_params: dict[str, str] | None = None
        self._headers: HttpHeaders | None = None
        self._cookies: dict[str, str] | None = None
        self._body: bytes | None = None
        self._json: dict | None = None

    @property
    def app(self):
        return self.scope.get('app')

    @property
    def scheme(self) -> str:
        return self.scope.get('scheme', 'http')

    @property
    def method(self) -> str:
        return self.scope['method']

    @property
    def path(self) -> str:
        return self.scope['path']

    @property
    def query_params(self) -> dict:
        if self._query_params is None:
            self._query_params: dict[str, str] = {}
            query_string = self.scope.get('query_string', b'').decode('latin1')

            for key, value in parse_qsl(query_string, keep_blank_values=True):
                self._query_params[key] = value
        return self._query_params

    @property
    def params(self) -> dict[str, Any]:
        return self.scope.get('params', {})

    @property
    def cookies(self) -> dict[str, str]:
        if self._cookies is None:
            cookies: dict[str, str] = {}
            cookie_header = self.headers.get('cookie')
            if cookie_header is not None:
                cookies = parse_cookie(cookie_header)
            self._cookies = cookies
        return self._cookies

    @property
    def headers(self) -> HttpHeaders:
        if self._headers is None:
            self._headers = HttpHeaders(self.scope['headers'])
        return self._headers

    async def stream(self) -> AsyncGenerator[bytes]:
        if self._body is not None:
            yield self._body
            yield b''
            return
        is_streaming: bool = True
        while is_streaming:
            message: Message = await self.receive()
            if message['type'] == 'http.disconnect':
                raise RequestAborted()
            if message['type'] == 'http.request':
                chunk: bytes = message.get('body', b'')
                if not message.get('more_body', False):
                    is_streaming = False
                yield chunk
        yield b''

    async def body(self) -> bytes:
        if self._body is None:
            chunks: bytearray = bytearray()
            async for chunk in self.stream():
                chunks.extend(chunk)
            self._body = bytes(chunks)
        return self._body

    async def json(self) -> dict:
        if self._json is None:
            self._json = json.loads(await self.body())
        return self._json
