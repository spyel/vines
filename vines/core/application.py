from typing import Any, Sequence, Callable

from vines.routing import Router, Route
from vines.middleware import Middleware
from vines.middleware.error import ServerErrorMiddleware, ExceptionMiddleware
from vines.http import HttpRequest, HttpResponse
from vines.core.types import Scope, Receive, Send


class Vines:
    """
    Creates an ASGI Application instance.

    **Parameters**
    - routes: A sequence of Route objects defining the application's routes.
    - middleware: A sequence of Middleware objects to be applied to requests.
    - settings: A dictionary of settings to override the default settings.
    """
    default_settings: dict[str, Any] = {
        'DEBUG': True,
    }

    def __init__(
        self,
        routes: Sequence[Route] | None = None,
        middleware: Sequence[Middleware] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        self.settings = Vines.default_settings | (settings or {})
        self.router = Router(
            path='/',
            routes=routes,
            middleware=[
                ServerErrorMiddleware(),
                ExceptionMiddleware()
            ] + list(middleware or [])
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Entrypoint for the ASGI application."""
        if not scope['type'] == 'http':
            raise ValueError(f'Vines can only handle ASGI/HTTP connections, not {scope['type']}.')

        scope['app'] = self

        request: HttpRequest = HttpRequest(scope, receive)
        response: HttpResponse = await self.router(request)
        await response(scope, receive, send)

    def route(self, path: str, methods: list[str] | None = None) -> Callable:
        return self.router.route(path, methods=methods)

    def get(self, path: str) -> Callable:
        return self.router.get(path)

    def post(self, path: str) -> Callable:
        return self.router.post(path)

    def put(self, path: str) -> Callable:
        return self.router.put(path)

    def patch(self, path: str) -> Callable:
        return self.router.patch(path)

    def delete(self, path: str) -> Callable:
        return self.router.delete(path)
