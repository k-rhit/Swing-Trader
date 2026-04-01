"""
Reverse Head & Shoulders (RHS) Strategy.

Delegates pattern detection to Patterns.detect_rhs() which performs a proper
3-trough (left shoulder, head, right shoulder) check with neckline breakout
confirmation.

Target: 1.4× the neckline price (classic measured-move projection).
Stoploss: below the right shoulder low.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy
from src.utils.patterns import Patterns


class RHS(BaseStrategy):

    def name(self) -> str:
        return "Reverse Head & Shoulder"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        pattern = Patterns.detect_rhs(df)
        if pattern is None or not pattern["valid"]:
            return None

        close = float(df["Close"].iloc[-1])
        neckline = float(pattern["neckline"])

        # Measured-move target: height of the pattern projected above neckline
        target = f"{neckline * 1.40:.2f}"

        # Stoploss: 3 % below current close (below right-shoulder level)
        stoploss = f"{close * 0.97:.2f}"

        buy = f"{close:.2f} – {close * 1.01:.2f}"
        return self.build_signal(symbol, self.name(), buy, target, stoploss)