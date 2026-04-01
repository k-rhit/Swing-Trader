"""
Backtest performance metrics.

Takes the list of result dicts from Backtester.run() and computes standard
trading-system statistics.
"""

from typing import List, Dict, Any
import statistics


class Metrics:

    @staticmethod
    def compute(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute summary statistics from backtest results.

        Args:
            results: Output of Backtester.run().

        Returns:
            Dict of performance metrics.
        """
        if not results:
            return {"signals": 0, "error": "No signals fired during backtest period."}

        returns = [r["forward_return_pct"] for r in results]
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]

        win_rate = len(wins) / len(returns) * 100 if returns else 0
        avg_win = statistics.mean(wins) if wins else 0
        avg_loss = statistics.mean(losses) if losses else 0
        profit_factor = (
            sum(wins) / abs(sum(losses)) if losses and sum(losses) != 0 else float("inf")
        )
        expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

        return {
            "signals": len(results),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate_pct": round(win_rate, 2),
            "avg_return_pct": round(statistics.mean(returns), 2),
            "avg_win_pct": round(avg_win, 2),
            "avg_loss_pct": round(avg_loss, 2),
            "best_trade_pct": round(max(returns), 2),
            "worst_trade_pct": round(min(returns), 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy_pct": round(expectancy, 2),
            "std_dev_pct": round(statistics.stdev(returns), 2) if len(returns) > 1 else 0,
        }