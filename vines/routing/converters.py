from typing import Any, Type, TypeVar, Generic

__all__ = ['Converter', 'get_converters', 'register_converter']


T = TypeVar('T')


class Converter(Generic[T]):
    regex: str = ''

    def to_value(self, value: str) -> T:
        raise NotImplementedError()

    def to_url(self, value: T) -> str:
        raise NotImplementedError()


class StringConverter(Converter[str]):
    regex = '[^/]+'

    def to_value(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return value


class PathConverter(StringConverter):
    regex = '.*'


class IntConverter(Converter[int]):
    regex = '[0-9]+'

    def to_value(self, value: str) -> int:
        return int(value)

    def to_url(self, value: int) -> str:
        return str(value)


class FloatConverter(Converter[float]):
    regex = r'[0-9]*\.?[0-9]+'

    def to_value(self, value: str) -> float:
        return float(value)

    def to_url(self, value: float) -> str:
        return str(value)


BUILTIN_CONVERTERS: dict[str, Converter] = {
    'str': StringConverter(),
    'path': PathConverter(),
    'int': IntConverter(),
    'float': FloatConverter(),
}

registered_converters: dict[str, Converter] = {}


def register_converter(name: str, converter: Type[Converter[Any]]) -> None:
    if name in registered_converters or name in BUILTIN_CONVERTERS:
        raise ValueError(f'Converter {name} is already registered.')
    registered_converters[name] = converter()


def get_converters() -> dict[str, Converter[Any]]:
    return {**BUILTIN_CONVERTERS, **registered_converters}
