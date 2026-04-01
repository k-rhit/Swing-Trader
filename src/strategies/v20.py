"""
V20 Strategy.

Identifies stocks that have risen more than 20 % over the last 5 trading days
in a sustained, uninterrupted uptrend (all 5 days positive).

Rationale: a clean, unbroken 5-day rally of 20 %+ signals strong institutional
momentum.  Entry is taken on the breakout bar; target is a continuation of the
same momentum leg.

Note: The original code used all(pct_change() > 0) which includes day-0 NaN.
Fixed by using .fillna(0) correctly and checking from day 1 onward.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy


class V20(BaseStrategy):

    def name(self) -> str:
        return "V20"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if len(df) < 10:
            return None

        recent = df.tail(6).copy()   # 6 rows → 5 pct_change values (first is NaN)
        pct = recent["Close"].pct_change().dropna()

        # All 5 days must close positive (unbroken uptrend)
        all_positive = (pct > 0).all()

        start_close = float(recent["Close"].iloc[0])
        end_close = float(recent["Close"].iloc[-1])

        # Total move over the 5-day window must be ≥ 20 %
        total_move = (end_close - start_close) / start_close
        strong_move = total_move >= 0.20

        if all_positive and strong_move:
            buy = f"{end_close:.2f}"
            # Conservative target: 10 % above entry (momentum continuation)
            target = f"{end_close * 1.10:.2f}"
            # Stoploss: below the lowest low of the 5-day run
            stoploss = f"{recent['Low'].min():.2f}"
            return self.build_signal(symbol, self.name(), buy, target, stoploss)

        return None