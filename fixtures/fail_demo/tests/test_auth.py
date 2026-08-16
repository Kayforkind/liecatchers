from unittest import mock

from src.auth import login


def test_auth():
    with mock.patch("src.auth.login") as m:
        m.return_value = True
        assert login() is True
