import pytest


def test_something():
    assert 2 + 2 == 4


class Testclass:
    def test_1(self):
        assert isinstance("test", str)
