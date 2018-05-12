import functools
import json
import sys
from typing import Callable, Tuple, Union

from .application import Application
from .request import Request
from .response import Response
from .server import HTTPServer

USERS = [
    {"id": 1, "name": "Jim"},
    {"id": 2, "name": "Bruce"},
    {"id": 3, "name": "Dick"},
]


def jsonresponse(handler: Callable[..., Union[dict, Tuple[str, dict]]]) -> Callable[..., Response]:
    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        result = handler(*args, **kwargs)
        if isinstance(result, tuple):
            status, result = result
        else:
            status, result = "200 OK", result

        response = Response(status=status)
        response.headers.add("content-type", "application/json")
        response.body.write(json.dumps(result).encode())
        return response
    return wrapper


app = Application()


@app.route("/users")
@jsonresponse
def get_users(request: Request) -> dict:
    return {"users": USERS}


@app.route("/users/{user_id}")
@jsonresponse
def get_user(request: Request, user_id: str) -> Union[dict, Tuple[str, dict]]:
    try:
        return {"user": USERS[int(user_id)]}
    except (IndexError, ValueError):
        return "404 Not Found", {"error": "Not found"}


def main() -> int:
    server = HTTPServer()
    server.mount("", app)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
