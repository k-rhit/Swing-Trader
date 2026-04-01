"""
Thin JSON persistence layer.

All paths are resolved relative to the project root (two levels above this
file) so the engine works regardless of the working directory from which it is
invoked.
"""

import json
import os
from typing import Any, List

# Project root: ai-swing-trader/
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _abs(path: str) -> str:
    """Return absolute path; relative paths are anchored to project root."""
    return path if os.path.isabs(path) else os.path.join(_ROOT, path)


class FileStore:

    @staticmethod
    def load(path: str) -> List[Any]:
        """Load a JSON list from *path*.  Returns [] if the file doesn't exist."""
        abs_path = _abs(path)
        if not os.path.exists(abs_path):
            return []
        with open(abs_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def save(path: str, data: Any) -> None:
        """Atomically write *data* as JSON to *path*."""
        abs_path = _abs(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        # Write to a temp file first so a crash never corrupts the store.
        tmp = abs_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
        os.replace(tmp, abs_path)