from typing import AsyncGenerator


def parse_options_header(header: str):
    options: dict[str, str] = {}

    parts: list[str] = header.split(';')
    content_type: str = parts[0].strip()

    for part in parts[1:]:
        if '=' in part:
            key, value = part.strip().split('=', maxsplit=1)
            options[key.lower()] = value.strip('"')

    return content_type, options


class MultiPartParserError(Exception):
    """Exception raised for errors in multipart parsing."""
    pass


class MultiPartParser:
    """A simple multipart parser for handling multipart/form-data requests."""

    def __init__(self, content_type_header: str, input_stream: AsyncGenerator[bytes]) -> None:
        content_type, options = parse_options_header(content_type_header)
        if not content_type == 'multipart/form-data':
            raise MultiPartParserError(f'Invalid content type: {content_type}')

        boundary: str = options.get('boundary')
        if not boundary:
            raise MultiPartParserError(f'Missing boundary in multipart: {content_type_header}.')

        self.input_stream: AsyncGenerator[bytes] = input_stream
        self.boundary: bytes = boundary.encode('ascii')
