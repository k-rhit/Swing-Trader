"""
Backtest runner — entry point for manual strategy evaluation.

Usage (from project root):
    python -m backtest.run_backtest
    python -m backtest.run_backtest --strategy sma --symbol RELIANCE --period 3y

Available strategy keys:
    sma, knoxville, v20, rhs, cwh, v10, lifetime, threex
"""

import argparse
import sys

import yfinance as yf
import pandas as pd

from backtest.engine.backtester import Backtester
from backtest.engine.metrics import Metrics
from backtest.engine.plot_results import plot_results


# ------------------------------------------------------------------
# Strategy registry
# ------------------------------------------------------------------
def _get_strategy(key: str):
    key = key.lower()
    if key == "sma":
        from src.strategies.sma_strategy import SMAStrategy
        return SMAStrategy()
    if key == "knoxville":
        from src.strategies.knoxville import Knoxville
        return Knoxville()
    if key == "v20":
        from src.strategies.v20 import V20
        return V20()
    if key == "rhs":
        from src.strategies.rhs import RHS
        return RHS()
    if key == "cwh":
        from src.strategies.cwh import CWH
        return CWH()
    if key == "v10":
        from src.strategies.v10 import V10
        return V10()
    if key == "lifetime":
        from src.strategies.lifetime_high import LifetimeHigh
        return LifetimeHigh()
    if key == "threex":
        from src.strategies.three_x_three_years import ThreeX
        return ThreeX()
    raise ValueError(f"Unknown strategy key: '{key}'. "
                     f"Choose from: sma, knoxville, v20, rhs, cwh, v10, lifetime, threex")


# ------------------------------------------------------------------
# Data fetch helper (flattens yfinance MultiIndex)
# ------------------------------------------------------------------
def _fetch(ticker: str, period: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d",
                     progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(subset=["Close"], inplace=True)
    return df


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Run a strategy backtest")
    parser.add_argument("--strategy", default="sma",
                        help="Strategy key (default: sma)")
    parser.add_argument("--symbol", default="RELIANCE",
                        help="NSE ticker without .NS (default: RELIANCE)")
    parser.add_argument("--period", default="3y",
                        help="yfinance period string (default: 3y)")
    parser.add_argument("--forward", type=int, default=10,
                        help="Forward bars for return measurement (default: 10)")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip chart generation")
    args = parser.parse_args()

    strategy = _get_strategy(args.strategy)
    ticker = args.symbol + ".NS"

    print(f"\n📊 Backtesting [{strategy.name()}] on {ticker} | period={args.period} | "
          f"forward={args.forward} bars\n")

    df = _fetch(ticker, args.period)
    if df.empty:
        print(f"❌ No data returned for {ticker}. Check the symbol and try again.")
        sys.exit(1)

    print(f"   Rows fetched: {len(df)}")

    # Run backtest
    bt = Backtester(forward_bars=args.forward)
    results = bt.run(df, strategy)

    # Print metrics
    metrics = Metrics.compute(results)
    print("\n── Performance Metrics ──────────────────────────")
    for k, v in metrics.items():
        print(f"   {k:<25} {v}")
    print("─────────────────────────────────────────────────\n")

    # Plot
    if not args.no_plot:
        plot_results(results, strategy_name=strategy.name())


if __name__ == "__main__":
    main()