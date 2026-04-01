"""
Centralised logger for the Swing Trader AI Engine.

Writes INFO+ to stdout and WARNING+ to a rotating file so CI logs stay clean
while disk logs capture only actionable events.
"""

import logging
import logging.handlers
import os

_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_LOG_FILE = os.path.join(_LOG_DIR, "swingtrader.log")

_fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(name)s — %(message)s")

# Console: INFO and above
_console = logging.StreamHandler()
_console.setLevel(logging.INFO)
_console.setFormatter(_fmt)

# File: WARNING and above, 5 MB × 3 backups
_file = logging.handlers.RotatingFileHandler(
    _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
)
_file.setLevel(logging.WARNING)
_file.setFormatter(_fmt)

logger = logging.getLogger("swingtrader")
logger.setLevel(logging.DEBUG)
logger.addHandler(_console)
logger.addHandler(_file)
logger.propagate = False  # prevent duplicate messages in root logger