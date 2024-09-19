import re

from vines.routing.converters import get_converters, Converter


PATH_REGEX = r'{(?:(?P<parameter>[^}:]+):)?(?P<converter>[^}]+)}'


def _route_to_regex(path: str) -> tuple[re.Pattern[str], dict[str, Converter]]:
    """Convert a path string with parameters into a regular expression pattern and map parameters to converters."""
    converter_types = get_converters()
    converters: dict[str, Converter] = {}
    regex: str = '^'

    previous: int = 0
    for match in re.finditer(PATH_REGEX, path):
        parameter, converter_type = match.groups(default='str')

        converter = converter_types.get(converter_type, None)
        if converter is None:
            raise Exception(
                f'Route {path} uses invalid converter {converter_type}.'
            )
        converters[parameter] = converter

        regex += re.escape(path[previous:match.start()])
        regex += f'(?P<{parameter}>{converter.regex})'

        previous = match.end()

    regex += re.escape(path[previous:])
    regex += '$'
    return re.compile(regex), converters
