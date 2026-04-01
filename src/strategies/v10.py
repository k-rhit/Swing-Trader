"""
V10 Strategy — Sharp V-shaped Reversal.

Delegates pattern detection to Patterns.detect_v10() which requires:
  1. A minimum 10 % intra-period drawdown over the last 20 bars.
  2. A full recovery back above the period's opening price.

This "V" shape (hard drop + full recovery) often signals that sellers are
exhausted and buyers have regained control.

Target: 10 % above the recovery close (continuation of bounce).
Stoploss: recent 5-bar swing low.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns


class V10(BaseStrategy):

    def name(self) -> str:
        return "V10"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        pattern = Patterns.detect_v10(df)
        if pattern is None or not pattern["valid"]:
            return None

        close = float(df["Close"].iloc[-1])
        drop_pct = pattern["drop_pct"]

        buy = f"{close:.2f}"
        target = f"{close * 1.10:.2f}"
        stoploss = f"{df['Low'].iloc[-5:].min():.2f}"

        # Embed the drop magnitude in the signal for context
        sig = self.build_signal(symbol, self.name(), buy, target, stoploss)
        sig["drop_pct"] = drop_pct   # extra metadata (stripped if not JSON-safe, but float is fine)
        return sig