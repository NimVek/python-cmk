import pytest

import cmk


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("title", "python-cmk"),
        ("summary", "API for CheckMK"),
        ("uri", "https://github.com/NimVek/python-cmk/"),
        ("author", "NimVek"),
        ("email", "NimVek@users.noreply.github.com"),
        ("license", "GPL-3.0-or-later"),
    ],
)
def test_about(key, value):
    assert getattr(cmk, f"__{key}__") == value
