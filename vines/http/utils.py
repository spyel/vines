import json
import datetime
from typing import Any


def parse_cookie(cookie: str) -> dict[str, str]:
    """Parse a cookie header string into a dictionary."""
    cookies: dict[str, str] = {}

    for pair in cookie.split(';'):
        pair = pair.strip()

        if '=' in pair:
            key, value = pair.split('=', 1)
        else:
            key, value = '', pair

        key, value = key.strip(), value.strip()

        if key or value:
            cookies[key] = value

    return cookies


class DateTimeEncoder(json.JSONEncoder):

    def default(self, o: Any) -> str:
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, datetime.time):
            return o.isoformat()

        return super().default(o)
