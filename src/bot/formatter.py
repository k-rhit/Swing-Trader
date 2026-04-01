"""
Telegram message formatter.

Produces human-readable, emoji-enhanced messages from signal dicts.
Kept separate from strategy logic so the presentation layer can evolve
independently.
"""

from typing import Dict, Any
import datetime


class Formatter:

    @staticmethod
    def signal(sig: Dict[str, Any]) -> str:
        """
        Render a signal dict as a Telegram-friendly text message.

        Args:
            sig: Dict with keys stock, strategy, buy, target, stoploss (optional).

        Returns:
            Formatted multi-line string.
        """
        today = datetime.date.today().strftime("%d %b %Y")
        stoploss = sig.get("stoploss", "—")
        return (
            f"📈 *BUY SIGNAL* — {today}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏷️  *Stock:*    {sig['stock']}\n"
            f"📐 *Strategy:* {sig['strategy']}\n"
            f"💰 *Buy Range:* ₹{sig['buy']}\n"
            f"🎯 *Target:*   ₹{sig['target']}\n"
            f"🛑 *Stoploss:* {stoploss}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

    @staticmethod
    def no_signals() -> str:
        today = datetime.date.today().strftime("%d %b %Y")
        return f"📭 No signals for {today}. Markets are quiet."