import typing

from collections import defaultdict


HeadersDict = typing.Dict[str, typing.List[str]]
HeadersGenerator = typing.Generator[typing.Tuple[str, str], None, None]


class Headers:
    def __init__(self) -> None:
        self._headers = defaultdict(list)

    def add(self, name: str, value: str) -> None:
        self._headers[name.lower()].append(value)

    def get_all(self, name: str) -> typing.List[str]:
        return self._headers[name.lower()]

    def get(self, name: str, default: typing.Optional[str] = None) -> typing.Optional[str]:
        try:
            return self.get_all(name)[-1]
        except IndexError:
            return default

    def __iter__(self) -> HeadersGenerator:
        return iter_headers(self._headers)


def iter_headers(headers: HeadersDict) -> HeadersGenerator:
    for name, values in headers.items():
        for value in values:
            yield name, value
