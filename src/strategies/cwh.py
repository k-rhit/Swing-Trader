"""
Cup With Handle (CWH) Strategy.

Delegates pattern detection to Patterns.detect_cwh() which checks for:
  - A U-shaped cup over the prior ~40 bars
  - A shallow handle consolidation (< 15 % depth) in the last 10 bars
  - A breakout close near/above the right rim of the cup

Target: 35 % above the breakout price (classic CWH measured-move target).
Stoploss: below the handle low.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns


class CWH(BaseStrategy):

    def name(self) -> str:
        return "Cup With Handle"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        pattern = Patterns.detect_cwh(df)
        if pattern is None or not pattern["valid"]:
            return None

        close = float(df["Close"].iloc[-1])

        # Handle low = minimum of last 10 bars — used as stoploss reference
        handle_low = float(df["Low"].iloc[-10:].min())

        buy = f"{close:.2f} – {close * 1.01:.2f}"
        target = f"{close * 1.35:.2f}"
        stoploss = f"{handle_low * 0.98:.2f}"   # slight buffer below handle low

        return self.build_signal(symbol, self.name(), buy, target, stoploss)