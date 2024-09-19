import inspect
import re
from typing import Any, Callable, Awaitable, Sequence

from vines.middleware import Middleware
from vines.routing.utils import _route_to_regex
from vines.http import HTTP_METHODS, HttpRequest, HttpResponse
from vines.http.exceptions import NotFoundException, MethodNotAllowedException


class BaseRoute:
    """The base class for defining routes."""

    def matches(self, path: str, method: str) -> tuple[bool, dict[str, Any]]:
        raise NotImplementedError()

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError()


class Route(BaseRoute):
    """Represents a single route that maps a URL path to an endpoint."""

    def __init__(
        self,
        path: str,
        endpoint: Callable[[HttpRequest], Awaitable[HttpResponse] | HttpResponse],
        methods: list[str] = None,
    ) -> None:
        assert path.startswith('/'), 'Routes must start with \'/\''

        self.path: str = path
        self.endpoint: Callable[[HttpRequest], Awaitable[HttpResponse] | HttpResponse] = endpoint
        self.methods: list[str] = list(methods or HTTP_METHODS)

        self._regex, self._converters = _route_to_regex(path)

    def matches(self, path: str, method: str) -> tuple[bool, dict[str, Any]]:
        match: re.Match[str] = self._regex.match(path)
        if match is None:
            return False, {}

        if method not in self.methods:
            return False, {'allowed_methods': self.methods}

        params = match.groupdict()
        for key, value in params.items():
            params[key] = self._converters[key].to_value(value)

        return True, {'params': params, 'sub_path': path}

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if inspect.iscoroutinefunction(self.endpoint):
            return await self.endpoint(request)
        return self.endpoint(request)


class Router(BaseRoute):
    """Represents a collection of routes, acting as a nested router."""

    def __init__(
        self,
        path: str,
        routes: Sequence[BaseRoute] | None = None,
        methods: list[str] | None = None,
        middleware: Sequence[Middleware] | None = None
    ) -> None:
        self.path: str = path
        self.routes: list[BaseRoute] = list(routes or [])
        self.methods: list[str] = list(methods or HTTP_METHODS)
        self.middleware: list[Middleware] = list(middleware or [])

        self._middleware_chain = None
        self._regex, self._converters = _route_to_regex(path + '/{path:path}')

    def add_route(
        self,
        path: str,
        endpoint: Callable[[HttpRequest], Awaitable[HttpResponse] | HttpResponse],
        methods: list[str] | None = None,
    ) -> None:
        self.routes.append(Route(path, endpoint, methods=methods))

    def add_router(
        self,
        path: str,
        routes: Sequence[BaseRoute] | None = None,
        methods: list[str] | None = None,
        middleware: Sequence[Middleware] | None = None,
    ) -> None:
        self.routes.append(Router(path, routes=routes, methods=methods, middleware=middleware))

    def route(self, path: str, methods: list[str] | None = None) -> Callable:
        def decorator(func: Callable[[HttpRequest], Awaitable[HttpResponse] | HttpResponse]) -> Callable:
            self.add_route(path, func, methods=methods)
            return func
        return decorator

    def build_middleware_chain(self) -> Callable[[HttpRequest], Awaitable[HttpResponse]]:
        chain = self.handle
        for mw in reversed(self.middleware):
            mw.call_next = chain
            chain = mw
        return chain

    def matches(self, path: str, method: str) -> tuple[bool, dict[str, Any]]:
        match: re.Match[str] = self._regex.match(path)
        if match is None:
            return False, {}

        if method not in self.methods:
            return False, {'allowed_methods': self.methods}

        params = match.groupdict()
        for key, value in params.items():
            params[key] = self._converters[key].to_value(value)
        remaining_path = '/' + params.pop('path')
        return True, {'params': params, 'sub_path': remaining_path}

    async def handle(self, request: HttpRequest) -> HttpResponse:
        path: str = request.scope.get('sub_path') or request.path

        allowed_methods: list[str] = []
        for route in self.routes:
            is_match, child_scope = route.matches(path, request.method)
            if not is_match:
                allowed_methods.extend(child_scope.get('allowed_methods', []))
                continue

            request.scope['params'] = child_scope['params']
            request.scope['sub_path'] = child_scope['sub_path']
            return await route(request)

        if len(allowed_methods) > 0:
            raise MethodNotAllowedException(request.method, allowed_methods=allowed_methods)

        raise NotFoundException(request.path)

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._middleware_chain is None:
            self._middleware_chain = self.build_middleware_chain()
        return await self._middleware_chain(request)
