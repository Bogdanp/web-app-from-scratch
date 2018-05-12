from typing import Dict, Generator, List, Optional, Tuple, overload

HeadersDict = Dict[str, List[str]]
HeadersGenerator = Generator[Tuple[str, str], None, None]


class Headers:
    _headers: HeadersDict

    def add(self, name: str, value: str) -> None:
        ...

    def get_all(self, name: str) -> List[str]:
        ...

    @overload
    def get(self, name: str) -> Optional[str]:
        ...

    @overload
    def get(self, name: str, default: str) -> str:
        ...

    def get_int(self, name: str) -> Optional[int]:
        ...

    def __iter__(self) -> HeadersGenerator:
        ...
