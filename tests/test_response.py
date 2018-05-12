import typing
from io import BytesIO
from textwrap import dedent

import pytest

from scratch.headers import Headers
from scratch.response import Response


class StubSocket:
    def __init__(self) -> None:
        self._buff = BytesIO()

    def sendall(self, data: bytes) -> None:
        self._buff.write(data)

    def sendfile(self, f: typing.IO[bytes]) -> None:
        self._buff.write(f.read())

    def getvalue(self) -> bytes:
        return self._buff.getvalue()


def make_output(s: str) -> str:
    return dedent(s).replace("\n", "\r\n").encode()


def make_headers(*headers) -> Headers:
    res = Headers()
    for name, value in headers:
        res.add(name, value)
    return res


@pytest.mark.parametrize("response,output", [
    [
        Response("200 OK"),
        make_output("""\
        HTTP/1.1 200 OK

        """)
    ],

    [
        Response("200 OK", headers=make_headers(
            ("content-type", "application/json"),
            ("content-length", "2"),
        ), content="{}"),
        make_output("""\
        HTTP/1.1 200 OK
        content-type: application/json
        content-length: 2

        {}""")
    ],

    [
        Response("200 OK", headers=make_headers(
            ("content-type", "text/html"),
            ("content-length", "5"),
        ), body=BytesIO(b"Hello")),
        make_output("""\
        HTTP/1.1 200 OK
        content-type: text/html
        content-length: 5

        Hello""")
    ],

    [
        Response(
            "200 OK",
            headers=make_headers(("content-type", "text/plain")),
            body=open("tests/fixtures/plain", "rb")
        ),
        make_output("""\
        HTTP/1.1 200 OK
        content-type: text/plain
        content-length: 5

        Hello""")
    ]
])
def test_response(response, output):
    socket = StubSocket()
    response.send(socket)
    assert socket.getvalue() == output
