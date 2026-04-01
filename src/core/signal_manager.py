"""
Signal deduplication and persistence.

Signals are stored as plain dicts (JSON-serialisable).  The "format" callable
that lives in BaseStrategy is intentionally stripped before saving — it is
re-hydrated by the Formatter when needed.
"""

from typing import List, Dict, Any
from src.utils.file_store import FileStore
from src.core.config import Config
from src.utils.logger import logger


class SignalManager:

    def __init__(self) -> None:
        self._state_path = Config.sent_signals_path()

    def filter_new_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Return only signals whose ID has not been sent before.

        Args:
            signals: List of signal dicts produced by BaseStrategy.build_signal().

        Returns:
            Subset of *signals* that are new (not in the persisted sent-log).
        """
        sent: List[Dict] = FileStore.load(self._state_path)
        sent_keys = {s["id"] for s in sent}

        new = [s for s in signals if s["id"] not in sent_keys]
        logger.info(f"Signals total={len(signals)}, new={len(new)}, already-sent={len(sent_keys)}")
        return new

    def save_sent_signals(self, new_signals: List[Dict[str, Any]]) -> None:
        """
        Append *new_signals* to the sent-log.

        The "format_fn" key (a callable) is excluded before serialisation
        because json.dump cannot handle Python functions.
        """
        if not new_signals:
            return

        sent: List[Dict] = FileStore.load(self._state_path)

        for sig in new_signals:
            # Strip the non-serialisable callable before persisting
            record = {k: v for k, v in sig.items() if k != "format_fn"}
            sent.append(record)

        FileStore.save(self._state_path, sent)
        logger.info(f"Saved {len(new_signals)} new signal(s) to sent log.")