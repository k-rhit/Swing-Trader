"""
Telegram notification bot.

Uses the sendMessage REST endpoint directly (no python-telegram-bot dependency)
to keep the requirements minimal.  Messages are sent with Markdown formatting.
"""

import time
import requests

from src.core.config import Config
from src.utils.logger import logger

_TIMEOUT = 10       # seconds per request
_MAX_RETRIES = 3    # attempts before giving up on a single message
_RETRY_DELAY = 2    # seconds between retries


class TelegramBot:

    def __init__(self) -> None:
        self._token = Config.tg_token()
        self._chat_id = Config.tg_chat_id()
        self._base_url = f"https://api.telegram.org/bot{self._token}"

    def send_message(self, text: str) -> bool:
        """
        Send *text* to the configured chat.

        Args:
            text: Message body (Markdown supported).

        Returns:
            True if the message was delivered, False otherwise.
        """
        url = f"{self._base_url}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "Markdown",   # enables bold/italic in formatted messages
        }

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(url, data=payload, timeout=_TIMEOUT)
                if resp.status_code == 200:
                    logger.debug("Telegram message delivered.")
                    return True
                else:
                    logger.warning(
                        f"Telegram returned HTTP {resp.status_code}: {resp.text} "
                        f"(attempt {attempt}/{_MAX_RETRIES})"
                    )
            except requests.RequestException as exc:
                logger.warning(f"Telegram request failed (attempt {attempt}/{_MAX_RETRIES}): {exc}")

            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY)

        logger.error(f"Failed to deliver Telegram message after {_MAX_RETRIES} attempts.")
        return False