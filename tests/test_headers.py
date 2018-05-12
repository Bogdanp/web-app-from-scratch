from scratch.headers import Headers


def test_can_add_headers():
    # Given that I have an empty Headers object
    headers = Headers()

    # When I add a header
    headers.add("x-a-header", "a value")

    # Then I should be able to get the value of that header back
    assert headers.get("x-a-header") == "a value"


def test_headers_are_case_insensitive():
    # Given that I have a Headers object
    headers = Headers()

    # And I've added a header that's all caps
    headers.add("X-A-HEADER", "a value")

    # When I get that header using its lower case name
    # Then I should get back its value
    assert headers.get("x-a-header") == "a value"


def test_getting_a_missing_header_returns_none():
    # Given that I have an empty Headers object
    headers = Headers()

    # When I get that some header
    # Then I should get back None
    assert headers.get("x-a-header") is None


def test_can_get_headers_with_fallback():
    # Given that I have an empty Headers object
    headers = Headers()

    # When I get that some header with a fallback value
    # Then I should get back that fallback value
    assert headers.get("x-a-header", "fallback") is "fallback"


def test_can_get_headers_as_ints():
    # Given that I have a Headers object
    headers = Headers()

    # And I've added a header with a stringy int value
    headers.add("content-length", "1024")

    # When I get that header as an int
    # Then I should get back its int value
    assert headers.get_int("content-length") == 1024


def test_can_get_headers_as_ints_with_fallback():
    # Given that I have an empty Headers object
    headers = Headers()

    # When I get some header as an int
    # Then I should get back None
    assert headers.get_int("content-length") is None


def test_getting_a_header_returns_its_last_value():
    # Given that I have a Headers object
    headers = Headers()

    # And I have added a header multiple times
    headers.add("x-some-header", "1")
    headers.add("x-some-header", "2")

    # When I get the value of that header
    # Then its last value should be returned
    assert headers.get("x-some-header") == "2"


def test_can_get_all_of_a_headers_values():
    # Given that I have a Headers object
    headers = Headers()

    # And I have added a header multiple times
    headers.add("x-some-header", "1")
    headers.add("x-some-header", "2")

    # When I get all of that header's values
    # Then I should get back a list containing each value
    assert headers.get_all("x-some-header") == ["1", "2"]


def test_headers_is_iterable():
    # Given that I have a Headers object
    headers = Headers()

    # And I've added a number of headers to it
    headers.add("content-type", "application/javascript")
    headers.add("content-length", "1024")
    headers.add("x-some-header", "1")
    headers.add("x-some-header", "2")

    # When I iterate over it
    # Then I should get back a sequence of name, value pairs
    assert sorted(list(headers)) == sorted([
        ("content-type", "application/javascript"),
        ("content-length", "1024"),
        ("x-some-header", "1"),
        ("x-some-header", "2"),
    ])
