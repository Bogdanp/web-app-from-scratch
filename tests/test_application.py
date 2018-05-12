from io import BytesIO

from scratch.application import Application
from scratch.headers import Headers
from scratch.request import Request
from scratch.response import Response

app = Application()


@app.route("/")
def static_handler(request):
    return Response(content="static")


@app.route("/people/{name}/{age}")
def dynamic_handler(request, name, age):
    return Response(content=f"{name} is {age} years old!")


def test_applications_can_route_requests():
    # Given that I have an application
    # When I request the static_handler
    response = app(Request(method="GET", path="/", headers=Headers(), body=BytesIO()))

    # Then I should get back a valid response
    assert response.body.read() == b"static"


def test_applications_can_route_requests_to_dynamic_paths():
    # Given that I have an application
    # When I request the dynamic_handler
    response = app(Request(method="GET", path="/people/Jim/32", headers=Headers(), body=BytesIO()))

    # Then I should get back a valid response
    assert response.body.read() == b"Jim is 32 years old!"


def test_applications_can_fail_to_route_invalid_paths():
    # Given that I have an application
    # When I request a path that isn't registered
    response = app(Request(method="GET", path="/invalid", headers=Headers(), body=BytesIO()))

    # Then I should get back a 404 response
    assert response.status == b"404 Not Found"
