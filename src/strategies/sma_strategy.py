"""
SMA 20/50/200 Strategy.

Signal condition: price is pulling back to the 20-day SMA while the trend is
aligned (SMA200 > SMA50 > SMA20), meaning the stock is in a healthy long-term
uptrend and offering a tactical entry.

Bug fixed: original code compared c.Close (scalar) to df["Low"].iloc[-1]
(also scalar after yfinance MultiIndex fix) with ==, which is fragile.
We now check that the current close is within 1 % of the daily low instead.
"""

from typing import Optional, Dict, Any
import pandas as pd
from src.strategies.base import BaseStrategy


class SMAStrategy(BaseStrategy):

    def name(self) -> str:
        return "SMA-20-50-200"

    def generate(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if len(df) < 200:
            return None  # Not enough history for SMA200

        df = df.copy()
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()

        last = df.iloc[-1]
        sma20 = last["SMA20"]
        sma50 = last["SMA50"]
        sma200 = last["SMA200"]
        close = float(last["Close"])
        low = float(last["Low"])

        # Trend alignment: long-term uptrend
        trend_ok = sma200 > sma50 > sma20

        # Pullback entry: close within 1 % above the day's low (weak intraday close)
        pullback = close <= low * 1.01

        # Price is near the SMA20 (within 2 %)
        near_sma20 = abs(close - sma20) / sma20 < 0.02

        if trend_ok and pullback and near_sma20:
            buy = f"{close:.2f} – {close * 1.01:.2f}"
            target = "Exit on MA reversal signal"
            stoploss = f"{low * 0.97:.2f}"  # 3 % below the day's low
            return self.build_signal(symbol, self.name(), buy, target, stoploss)

        return None