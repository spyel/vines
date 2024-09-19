from typing import Callable, Awaitable

from vines.http import HttpRequest, HttpResponse


class Middleware:
    """Base class for ASGI Middleware, allowing request and response processing."""
    call_next: Callable[[HttpRequest], Awaitable[HttpResponse]]

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handles the incoming request and processes it through the middleware chain."""
        if self.call_next is None:
            raise RuntimeError(
                'Middleware Error: \'call_next\' is not set. Ensure the middleware is properly initialized.'
            )

        response = self.process_request(request)
        if response is not None:
            return response

        response = await self.call_next(request)
        return self.process_response(request, response)

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Processes the incoming request before passing it to the next middleware or endpoint."""
        raise None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Processes the response before it is returned to the client."""
        return response
