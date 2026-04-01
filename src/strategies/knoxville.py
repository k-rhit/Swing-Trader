"""
Knoxville Divergence Strategy.

A bearish-RSI / bullish-momentum divergence setup popularised by Rob Smith.
Signal fires when:
  - RSI(14) is oversold (< 40) suggesting price weakness
  - 20-bar price momentum is positive (price is actually rising)

This divergence (price momentum positive while oscillator is weak) often
precedes a sharp reversal upward.

Bug fixed: original code used pct_change().rolling(14).mean() for RSI which
is not RSI at all.  Replaced with a standard Wilder-smoothed RSI.
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from src.strategies.base import BaseStrategy


def _wilder_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI using Wilder's exponential smoothing (standard formula)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


class Knoxville(BaseStrategy):

    def name(self) -> str:
        return "Knoxville Divergence"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if len(df) < 30:
            return None

        rsi = _wilder_rsi(df["Close"], period=14)
        momentum = df["Close"].diff(20)   # 20-bar rate of change (price diff)

        current_rsi = float(rsi.iloc[-1])
        current_mom = float(momentum.iloc[-1])

        # Knoxville divergence: RSI weak but price momentum turning positive
        if current_rsi < 40 and current_mom > 0:
            close = float(df["Close"].iloc[-1])
            buy = f"{close:.2f}"
            target = "Next Knoxville uptrend confirmation"
            stoploss = f"{df['Low'].iloc[-5:].min():.2f}"   # recent swing low
            return self.build_signal(symbol, self.name(), buy, target, stoploss)

        return None