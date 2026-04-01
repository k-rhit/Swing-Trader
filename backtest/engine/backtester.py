"""
Walk-forward backtester.

Slides a growing window over historical data, invoking the strategy at each
bar as if it were "today".  Collects all signals and computes forward returns
so we can measure strategy performance without look-ahead bias.

Usage:
    bt = Backtester(forward_bars=10)
    results = bt.run(df, strategy)
"""

from typing import List, Dict, Any
import pandas as pd
from src.utils.logger import logger


class Backtester:

    def __init__(self, forward_bars: int = 10, min_history: int = 200) -> None:
        """
        Args:
            forward_bars: How many bars ahead to measure the signal's return.
            min_history:  Minimum bars of history before starting the walk.
        """
        self.forward_bars = forward_bars
        self.min_history = min_history

    def run(self, df: pd.DataFrame, strategy) -> List[Dict[str, Any]]:
        """
        Walk-forward scan over *df* using *strategy*.

        For every bar from min_history onward, the strategy sees only data up
        to that bar.  If a signal fires, we record the entry price and the
        forward return after *forward_bars* bars.

        Args:
            df:       Full historical OHLCV DataFrame.
            strategy: Any BaseStrategy instance.

        Returns:
            List of result dicts, one per signal fired.
        """
        results = []
        total_bars = len(df)

        logger.info(
            f"Backtest [{strategy.name()}]: {total_bars} bars, "
            f"walk starting at bar {self.min_history}, "
            f"forward window = {self.forward_bars} bars"
        )

        for i in range(self.min_history, total_bars - self.forward_bars):
            window = df.iloc[:i]

            try:
                signal = strategy.generate(window, "BACKTEST")
            except Exception as exc:
                logger.debug(f"Strategy error at bar {i}: {exc}")
                continue

            if signal is None:
                continue

            entry_price = float(df["Close"].iloc[i])
            exit_price = float(df["Close"].iloc[i + self.forward_bars])

            forward_return_pct = (exit_price - entry_price) / entry_price * 100

            results.append({
                "bar": i,
                "date": str(df.index[i].date()),
                "strategy": strategy.name(),
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "forward_return_pct": round(forward_return_pct, 2),
                "signal_buy": signal.get("buy"),
                "signal_target": signal.get("target"),
            })

        logger.info(f"Backtest complete: {len(results)} signals fired")
        return results