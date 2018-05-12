import logging
import mimetypes
import os
import socket
import typing
from queue import Empty, Queue
from threading import Thread
from typing import Callable, List, Tuple

from request import Request
from response import Response

LOGGER = logging.getLogger(__name__)

HandlerT = Callable[[Request], Response]


class HTTPWorker(Thread):
    def __init__(self, connection_queue: Queue, handlers: List[Tuple[str, HandlerT]]) -> None:
        super().__init__(daemon=True)

        self.connection_queue = connection_queue
        self.handlers = handlers
        self.running = False

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            try:
                client_sock, client_addr = self.connection_queue.get(timeout=1)
            except Empty:
                continue

            try:
                self.handle_client(client_sock, client_addr)
            except Exception:
                LOGGER.exception("Unhandled error in handle_client.")
                continue
            finally:
                self.connection_queue.task_done()

    def handle_client(self, client_sock: socket.socket, client_addr: typing.Tuple[str, int]) -> None:
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
            except Exception:
                LOGGER.warning("Failed to parse request.", exc_info=True)
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_sock)
                return

            # Force clients to send their request bodies on every
            # request rather than making the handlers deal with this.
            if "100-continue" in request.headers.get("expect", ""):
                response = Response(status="100 Continue")
                response.send(client_sock)

            for path_prefix, handler in self.handlers:
                if request.path.startswith(path_prefix):
                    try:
                        request = request._replace(path=request.path[len(path_prefix):])
                        response = handler(request)
                        response.send(client_sock)
                    except Exception as e:
                        LOGGER.exception("Unexpected error from handler %r.", handler)
                        response = Response(status="500 Internal Server Error", content="Internal Error")
                        response.send(client_sock)
                    finally:
                        break
            else:
                response = Response(status="404 Not Found", content="Not Found")
                response.send(client_sock)


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=9000, worker_count=16) -> None:
        self.handlers: List[Tuple[str, HandlerT]] = []
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.worker_backlog = worker_count * 8
        self.connection_queue: Queue = Queue(self.worker_backlog)

    def mount(self, path_prefix: str, handler: HandlerT) -> None:
        """Mount a request handler at a particular path.  Handler
        prefixes are tested in the order that they are added so the
        first match "wins".
        """
        self.handlers.append((path_prefix, handler))

    def serve_forever(self) -> None:
        workers = []
        for _ in range(self.worker_count):
            worker = HTTPWorker(self.connection_queue, self.handlers)
            worker.start()
            workers.append(worker)

        with socket.socket() as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(self.worker_backlog)
            LOGGER.info("Listening on %s:%d...", self.host, self.port)

            while True:
                try:
                    self.connection_queue.put(server_sock.accept())
                except KeyboardInterrupt:
                    break

        for worker in workers:
            worker.stop()

        for worker in workers:
            worker.join(timeout=30)


def serve_static(server_root: str) -> HandlerT:
    """Generate a request handler that serves file off of disk
    relative to server_root.
    """

    def handler(request: Request) -> Response:
        path = request.path
        if request.path == "/":
            path = "/index.html"

        abspath = os.path.normpath(os.path.join(server_root, path.lstrip("/")))
        if not abspath.startswith(server_root):
            return Response(status="404 Not Found", content="Not Found")

        try:
            content_type, encoding = mimetypes.guess_type(abspath)
            if content_type is None:
                content_type = "application/octet-stream"

            if encoding is not None:
                content_type += f"; charset={encoding}"

            body_file = open(abspath, "rb")
            response = Response(status="200 OK", body=body_file)
            response.headers.add("content-type", content_type)
            return response
        except FileNotFoundError:
            return Response(status="404 Not Found", content="Not Found")

    return handler


def wrap_auth(handler: HandlerT) -> HandlerT:
    def auth_handler(request: Request) -> Response:
        authorization = request.headers.get("authorization", "")
        if authorization.startswith("Bearer ") and authorization[len("Bearer "):] == "opensesame":
            return handler(request)
        return Response(status="403 Forbidden", content="Forbidden!")
    return auth_handler


def app(request: Request) -> Response:
    return Response(content="Hello!")


server = HTTPServer()
server.mount("/static", serve_static("www"))
server.mount("", wrap_auth(app))
server.serve_forever()
