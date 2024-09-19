import io
from typing import Any, Sequence, Callable, Awaitable, IO

from vines.routing import Router, Route
from vines.middleware import Middleware
from vines.middleware.error import ServerErrorMiddleware, ExceptionMiddleware
from vines.http import HttpRequest, HttpResponse
from vines.core.exceptions import RequestAborted


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

    def route(self, path: str, methods: list[str] | None = None) -> Callable:
        def decorator(func: Callable[[HttpRequest], Awaitable[HttpResponse] | HttpResponse]) -> Callable:
            self.router.add_route(path, func, methods=methods)
            return func
        return decorator

    async def handle(self, scope, receive, send) -> None:
        """Handles the ASGI request. Called via the __call__ method."""
        body_file = await self.read_body(receive)

        request: HttpRequest = HttpRequest(scope, body_file)
        response: HttpResponse = await self.router(request)

        await send({
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': response.headers.encode()}
        )
        await send({'type': 'http.response.body', 'body': response.body})

    async def read_body(self, receive):
        """Reads an HTTP body from an ASGI connection."""
        is_streaming: bool = True
        body_file: IO = io.BytesIO()
        while is_streaming:
            message = await receive()

            if message['type'] == 'http.disconnect':
                body_file.close()
                raise RequestAborted()

            body_file.write(message.get('body', b''))

            if not message.get('more_body', False):
                is_streaming = False

        body_file.seek(0)
        return body_file

    async def __call__(self, scope, receive, send) -> None:
        """Entrypoint for the ASGI application."""
        if not scope['type'] == 'http':
            raise ValueError(f'Vines can only handle ASGI/HTTP connections, not {scope['type']}.')

        scope['app'] = self
        await self.handle(scope, receive, send)
