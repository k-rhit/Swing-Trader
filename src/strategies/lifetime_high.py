"""
Lifetime High Strategy.

Identifies stocks that are significantly below their all-time high (within the
available data window) and may be setting up for a recovery trade.

Signal condition: current close is ≤ 70 % of the historical high.
Target: the historical high (full recovery).
Stoploss: 10 % below current price.

Note: "lifetime" high is limited to the yfinance download window (default 3y).
For a true lifetime high, extend FETCH_PERIOD to "max" in Config or env vars.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy


class LifetimeHigh(BaseStrategy):

    def name(self) -> str:
        return "Lifetime High"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if len(df) < 20:
            return None

        all_time_high = float(df["High"].max())
        close = float(df["Close"].iloc[-1])

        # Entry only when price is at least 30 % off the high
        discount = (all_time_high - close) / all_time_high
        if discount < 0.30:
            return None

        buy = f"{close:.2f}"
        target = f"{all_time_high:.2f}"
        stoploss = f"{close * 0.90:.2f}"   # 10 % trailing stop

        return self.build_signal(symbol, self.name(), buy, target, stoploss)