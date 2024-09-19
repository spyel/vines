from vines.http.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

__all__ = ['HttpException', 'NotFoundException', 'MethodNotAllowedException']


class HttpException(Exception):
    status_code = HTTP_400_BAD_REQUEST
    message = ''
    detail = ''

    def __init__(self, status: int | None = None, message: str | None = None, detail: str | None = None) -> None:
        self.status_code = status or self.status_code
        self.message = message or self.message
        self.detail = detail or self.detail

    def __str__(self) -> str:
        return self.detail


class NotAuthenticatedException(HttpException):
    status_code = HTTP_401_UNAUTHORIZED
    message = 'Authentication credentials were not provided.'
    detail = 'Not Authenticated'


class PermissionDeniedException(HttpException):
    status_code = HTTP_403_FORBIDDEN
    message = 'Permission Denied'
    detail = 'You do not have permission to perform this action.'


class NotFoundException(HttpException):
    status_code = HTTP_404_NOT_FOUND
    message = 'Not Found'
    detail = 'The requested resource at \'%s\' could not be found.'

    def __init__(self, path: str) -> None:
        self.detail = self.detail % path


class MethodNotAllowedException(HttpException):
    status_code = HTTP_405_METHOD_NOT_ALLOWED
    message = 'Method not allowed'
    detail = 'Method "%s" is not allowed.'

    def __init__(self, method: str, allowed_methods: list[str]) -> None:
        self.allowed_methods = allowed_methods
        self.detail = self.detail % method
