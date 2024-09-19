import json
from datetime import datetime, timedelta
from typing import Any, Type, Literal, MutableMapping

from vines.http import status as http_status
from vines.http.utils import DateTimeEncoder


class HttpResponseHeaders(MutableMapping[str, str]):
    """
    A class to represent and manage HTTP response headers with case-insensitive keys.
    Supports header manipulation and cookie management.
    """

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        self._headers: dict[str, str] = {}
        self._cookies: list[str] = []

        for key, value in (headers or {}).items():
            self[key] = value

    def __setitem__(self, key: str, value: str) -> None:
        self._headers[key.lower()] = value

    def __getitem__(self, key: str) -> str:
        return self._headers[key.lower()]

    def __delitem__(self, key: str) -> None:
        self._headers.pop(key.lower())

    def __iter__(self) -> iter:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def __repr__(self) -> str:
        return str(self._headers)

    def has(self, key: str) -> bool:
        return key.lower() in self._headers

    def set_cookie(
        self,
        key: str,
        value: str,
        path: str = '/',
        domain: str | None = None,
        max_age: int | None = None,
        expires: str | int | None = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Literal['lax', 'strict', 'none'] | None = None
    ) -> None:
        cookie = f'{key}={value}; Path={path}'

        if domain is not None:
            cookie += f'; Domain={domain}'
        if max_age is not None:
            cookie += f'; Max-Age={max_age}'
        if expires is not None:
            if isinstance(expires, int):
                time = datetime.now() + timedelta(seconds=expires)
                expires = time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            cookie += f'; Expires={expires}'
        if secure:
            cookie += f'; Secure'
        if http_only:
            cookie += f'; HttpOnly'
        if same_site is not None:
            cookie += f'; SameSite={same_site.capitalize()}'

        self._cookies.append(cookie)

    def delete_cookie(self, key: str, path: str = '/', domain: str | None = None) -> None:
        self.set_cookie(key, '', path=path, domain=domain, max_age=0, expires=0)

    def encode(self) -> list[tuple[bytes, bytes]]:
        """Convert headers to a list of byte-encoded key-value tuples."""
        data: list[tuple[bytes, bytes]] = []
        for key, value in self._headers.items():
            data.append((key.encode('ascii'), value.encode('latin1')))

        for cookie in self._cookies:
            data.append((b'set-cookie', cookie.encode('latin1')))

        return data


class HttpResponse:

    def __init__(
        self,
        content: Any = None,
        status_code: int | None = None,
        content_type: str | None = None,
        charset: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._content: Any = content
        self._charset: str | None = charset
        self._body_cache: bytes | None = None

        self.headers = HttpResponseHeaders(headers)
        media_type = f'text/plain; charset={self.charset}'
        if content_type is not None:
            media_type = f'{content_type}; charset={self.charset}'
        self.headers['content-type'] = media_type
        self.headers['content-length'] = str(len(self.body))

        if status_code is None:
            status_code = http_status.HTTP_200_OK
        self.status_code = status_code

    @property
    def charset(self) -> str:
        return self._charset or 'utf-8'

    @property
    def content_type(self) -> str:
        return self.headers['content-type']

    @property
    def content(self) -> Any:
        return self._content

    @property
    def body(self) -> bytes:
        if self._body_cache is not None:
            return self._body_cache
        
        if self._content is None:
            return b''
        if isinstance(self._content, (bytes, memoryview)):
            return bytes(self._content)
        if isinstance(self._content, str):
            return self._content.encode(self.charset)
        return str(self._content).encode(self.charset)


class JSONResponse(HttpResponse):

    def __init__(
        self,
        content: dict,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        encoder: Type[json.JSONEncoder] = DateTimeEncoder,
    ) -> None:
        super().__init__(
            json.dumps(content, cls=encoder),
            status_code=status_code,
            content_type='application/json',
            headers=headers
        )
