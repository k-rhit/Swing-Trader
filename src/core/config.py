"""
Central configuration.

All environment variables are read here so the rest of the codebase never
calls os.getenv() directly.  Paths are resolved relative to the project root
so the engine runs correctly regardless of the working directory.
"""

import os
import json
from typing import List

# Project root: two levels above this file (src/core/config.py → root)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _data_path(filename: str) -> str:
    """Return the absolute path to a file in src/data/."""
    return os.path.join(_ROOT, "src", "data", filename)


class Config:

    # ------------------------------------------------------------------
    # Telegram credentials (read from environment / GitHub Secrets)
    # ------------------------------------------------------------------
    @staticmethod
    def tg_token() -> str:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            raise EnvironmentError(
                "TELEGRAM_BOT_TOKEN is not set. "
                "Add it as a GitHub Secret or export it in your shell."
            )
        return token

    @staticmethod
    def tg_chat_id() -> str:
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if not chat_id:
            raise EnvironmentError(
                "TELEGRAM_CHAT_ID is not set. "
                "Add it as a GitHub Secret or export it in your shell."
            )
        return chat_id

    # ------------------------------------------------------------------
    # Symbol lists
    # ------------------------------------------------------------------
    @staticmethod
    def load_symbols(list_name: str = "symbols_all") -> List[str]:
        """
        Load a symbol list from src/data/<list_name>.json.

        Args:
            list_name: JSON file stem, e.g. "v40_list", "symbols_all".

        Returns:
            List of ticker strings (without the .NS suffix).
        """
        path = _data_path(f"{list_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Symbol list not found: {path}\n"
                "Create src/data/symbols_all.json with a JSON array of ticker strings."
            )
        with open(path, "r", encoding="utf-8") as fh:
            symbols = json.load(fh)
        if not isinstance(symbols, list):
            raise ValueError(f"{path} must contain a JSON array of strings.")
        return symbols

    # ------------------------------------------------------------------
    # Misc tunables (can be overridden via env vars)
    # ------------------------------------------------------------------
    @staticmethod
    def fetch_period() -> str:
        """yfinance period for daily data fetch (default: 3y for multi-year strategies)."""
        return os.getenv("FETCH_PERIOD", "3y")

    @staticmethod
    def sent_signals_path() -> str:
        """Absolute path to the sent-signals state file."""
        return os.path.join(_ROOT, "sent_signals.json")