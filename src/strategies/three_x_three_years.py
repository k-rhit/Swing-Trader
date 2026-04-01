"""
3× in 3 Years Strategy.

Identifies stocks that have fallen to ≤ 33 % of their 3-year high, meaning
they would need to 3× from the current price just to reach their prior peak.

These deep-value setups carry high risk but also high reward if the business
recovers.  Use only with strong fundamental conviction.

Signal condition: close ≤ 33 % of 3-year high.
Target: the 3-year high.
Stoploss: 15 % below entry (wide stop for a deep-value thesis).

Note: Requires at least 500 trading days (~2 years) of data to be meaningful.
      Set FETCH_PERIOD=3y (default) or "max" for best results.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy


_MIN_BARS = 500   # ~2 years of trading days


class ThreeX(BaseStrategy):

    def name(self) -> str:
        return "3X in 3 Years"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if len(df) < _MIN_BARS:
            # Not enough history — skip rather than generate a misleading signal
            return None

        three_year_high = float(df["High"].max())
        close = float(df["Close"].iloc[-1])

        # Price must be at or below one-third of the 3-year peak
        if close > three_year_high * 0.33:
            return None

        potential_return = three_year_high / close  # e.g. 3.2 → "3.2× potential"

        buy = f"{close:.2f}"
        target = f"{three_year_high:.2f}"
        stoploss = f"{close * 0.85:.2f}"   # 15 % stop for a deep-value thesis

        sig = self.build_signal(symbol, self.name(), buy, target, stoploss)
        sig["potential_return"] = round(potential_return, 2)   # e.g. 3.5
        return sig