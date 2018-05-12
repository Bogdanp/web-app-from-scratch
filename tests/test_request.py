from io import BytesIO
from textwrap import dedent

import pytest

from scratch.request import Request


class StubSocket:
    def __init__(self, data: str):
        self._buff = BytesIO(data.encode())

    def recv(self, n: int) -> bytes:
        return self._buff.read(n)


def make_request(s: str) -> str:
    return dedent(s).replace("\n", "\r\n")


@pytest.mark.parametrize("data,method,path,headers,body", [
    [
        make_request("""\
        GET / HTTP/1.0
        Accept: text/html

        """),

        "GET", "/", [("accept", "text/html")], b"",
    ],
    [
        make_request("""\
        POST /users HTTP/1.0
        Accept: application/json
        Content-type: application/json
        Content-length: 2

        {}"""),

        "POST",
        "/users",
        [
            ("accept", "application/json"),
            ("content-type", "application/json"),
            ("content-length", "2"),
        ],
        b"{}",
    ],
])
def test_requests(data, method, path, headers, body):
    request = Request.from_socket(StubSocket(data))
    assert request.method == method
    assert request.path == path
    assert sorted(list(request.headers)) == sorted(headers)
    assert request.body.read(16384) == body


@pytest.mark.parametrize("data,error", [
    [
        "",
        ValueError("Request line missing."),
    ],

    [
        make_request("""\
        GET
        """),
        ValueError("Malformed request line 'GET'."),
    ],

    [
        make_request("""\
        GET / HTTP/1.0
        Content-type
        """),
        ValueError("Malformed header line b'Content-type'."),
    ],
])
def test_invalid_requests(data, error):
    with pytest.raises(type(error)) as e:
        Request.from_socket(StubSocket(data))

    assert e.value.args == error.args
