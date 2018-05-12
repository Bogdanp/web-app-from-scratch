import pytest

from scratch.application import Router
from scratch.response import Response


def test_router_can_add_routes():
    # Given that I have a Router object
    router = Router()

    # And a route handler
    def get_example(request):
        return Response()

    # When I add a static route to it
    router.add_route("get_example", "GET", "/example", get_example)

    # Then I should be able to look it up using its path and method
    assert router.lookup("GET", "/missing") is None
    assert router.lookup("GET", "/example").func is get_example


def test_router_can_add_routes_with_dynamic_segments():
    # Given that I have a Router object
    router = Router()

    # And a route handler
    def get_example(name):
        return name

    # When I add a dynamic route to it
    router.add_route("get_example", "GET", "/users/{name}", get_example)

    # Then I should be able to look it up
    handler = router.lookup("GET", "/users/Jim")
    assert handler.func is get_example

    # And it should have its dynamic segments partially-applied
    assert handler() == "Jim"


def test_router_fails_to_add_routes_with_duplicate_names():
    # Given that I have a Router object
    router = Router()

    # And a route handler
    def get_example(name):
        return name

    # When I add two routes with the same name
    # Then I should get back a value error
    with pytest.raises(ValueError):
        router.add_route("get_example", "GET", "/users/{name}", get_example)
        router.add_route("get_example", "GET", "/users/{name}", get_example)
