from collections import defaultdict


class Headers:
    """A mapping from lower-cased header names to lists of string values.
    """

    def __init__(self):
        self._headers = defaultdict(list)

    def add(self, name, value):
        self._headers[name.lower()].append(value)

    def get_all(self, name):
        return self._headers[name.lower()]

    def get(self, name, default=None):
        try:
            return self.get_all(name)[-1]
        except IndexError:
            return default

    def get_int(self, name):
        try:
            return int(self.get(name))
        except (TypeError, ValueError):
            return None

    def __iter__(self):
        for name, values in self._headers.items():
            for value in values:
                yield name, value
