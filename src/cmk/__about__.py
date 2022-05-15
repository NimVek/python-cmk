"""Provides python-cmk various information."""
from __future__ import annotations

from ._version import __version__ as version


__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

__title__ = "python-cmk"
__summary__ = "API for CheckMK"
__uri__ = "https://github.com/NimVek/python-cmk/"

__version__ = version.short()

__author__ = "NimVek"
__email__ = "NimVek@users.noreply.github.com"

__license__ = "GPL-3.0-or-later"
