"""Helper for mkdocs to prepare docs-Directory."""

import os.path
import shutil


def on_pre_build(config):
    """Copy some files to docs dir.

    Args:
        config: global configuration object
    """
    del config

    _copy = {
        "index.md": "README.md",
        "LICENSE.md": "LICENSE.md",
        "CHANGELOG.md": "CHANGELOG.md",
    }

    for target, source in _copy.items():
        if not os.path.isfile(f"docs/{target}") and os.path.isfile(source):
            shutil.copy(source, f"docs/{target}")
