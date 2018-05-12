import re
from collections import OrderedDict, defaultdict
from functools import partial
from typing import Callable, Dict, Optional, Pattern, Set, Tuple

from .request import Request
from .response import Response
from .server import HandlerT

RouteT = Tuple[Pattern[str], HandlerT]
RoutesT = Dict[str, Dict[str, RouteT]]
RouteHandlerT = Callable[..., Response]


class Router:
    def __init__(self) -> None:
        self.routes_by_method: RoutesT = defaultdict(OrderedDict)
        self.route_names: Set[str] = set()

    def add_route(self, name: str, method: str, path: str, handler: RouteHandlerT) -> None:
        assert path.startswith("/"), "paths must start with '/'"
        if name in self.route_names:
            raise ValueError(f"A route named {name} already exists.")

        route_template = ""
        for segment in path.split("/")[1:]:
            if segment.startswith("{") and segment.endswith("}"):
                segment_name = segment[1:-1]
                route_template += f"/(?P<{segment_name}>[^/]+)"
            else:
                route_template += f"/{segment}"

        route_re = re.compile(f"^{route_template}$")
        self.routes_by_method[method][name] = route_re, handler
        self.route_names.add(name)

    def lookup(self, method: str, path: str) -> Optional[HandlerT]:
        for route_re, handler in self.routes_by_method[method].values():
            match = route_re.match(path)
            if match is not None:
                params = match.groupdict()
                return partial(handler, **params)
        return None


class Application:
    def __init__(self) -> None:
        self.router = Router()

    def add_route(self, method: str, path: str, handler: RouteHandlerT, name: Optional[str] = None) -> None:
        self.router.add_route(name or handler.__name__, method, path, handler)

    def route(
            self,
            path: str,
            method: str = "GET",
            name: Optional[str] = None,
    ) -> Callable[[RouteHandlerT], RouteHandlerT]:
        def decorator(handler: RouteHandlerT) -> RouteHandlerT:
            self.add_route(method, path, handler, name)
            return handler
        return decorator

    def __call__(self, request: Request) -> Response:
        handler = self.router.lookup(request.method, request.path)
        if handler is None:
            return Response("404 Not Found", content="Not Found")
        return handler(request)
