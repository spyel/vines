import traceback

from vines.middleware import Middleware
from vines.http import HttpRequest, HttpResponse, JSONResponse
from vines.http.exceptions import HttpException, MethodNotAllowedException


class ServerErrorMiddleware(Middleware):

    async def __call__(self, request: HttpRequest) -> HttpResponse | None:
        try:
            return await self.call_next(request)
        except Exception as e:
            app = request.app

            content = {
                'status': 500,
                'message': 'Internal Server Error',
                'detail': 'An unexpected error occurred on the server.'
            }

            if not app.settings['DEBUG']:
                response = JSONResponse(content, status_code=500)
                return response

            content['detail'] = str(e)
            content['traceback'] = traceback.format_exc().splitlines()
            response = JSONResponse(content, status_code=500)
            return response


class ExceptionMiddleware(Middleware):

    async def __call__(self, request: HttpRequest) -> HttpResponse | None:
        try:
            response = await self.call_next(request)
            return response
        except MethodNotAllowedException as e:
            response = JSONResponse(
                content={
                    'status': e.status_code,
                    'message': e.message,
                    'detail': e.detail,
                    'allowed_methods': e.allowed_methods
                },
                status_code=e.status_code,
            )
            response.headers['Allow'] = ', '.join(e.allowed_methods)
            return response
        except HttpException as e:
            response = JSONResponse(
                content={
                    'status': e.status_code,
                    'message': e.message,
                    'detail': e.detail,
                },
                status_code=e.status_code
            )
            return response
