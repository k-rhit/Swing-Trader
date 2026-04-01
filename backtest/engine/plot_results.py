"""
Backtest result visualisation.

Generates two charts:
  1. Equity curve — cumulative return over time
  2. Return distribution — histogram of per-trade forward returns
"""

from typing import List, Dict, Any
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def plot_results(results: List[Dict[str, Any]], strategy_name: str = "Strategy") -> None:
    """
    Save equity-curve and return-distribution charts to backtest/output/.

    Args:
        results:       Output of Backtester.run().
        strategy_name: Used in chart titles and filenames.
    """
    if not results:
        print("No results to plot.")
        return

    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    returns = [r["forward_return_pct"] for r in results]
    dates = [r["date"] for r in results]

    # ------------------------------------------------------------------
    # 1. Equity Curve (cumulative sum of forward returns)
    # ------------------------------------------------------------------
    cumulative = []
    total = 0.0
    for ret in returns:
        total += ret
        cumulative.append(total)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Backtest Results — {strategy_name}", fontsize=14, fontweight="bold")

    ax1 = axes[0]
    ax1.plot(range(len(cumulative)), cumulative, color="#2196F3", linewidth=1.5)
    ax1.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax1.fill_between(
        range(len(cumulative)), cumulative, 0,
        where=[c >= 0 for c in cumulative], color="#4CAF50", alpha=0.2, label="Profit"
    )
    ax1.fill_between(
        range(len(cumulative)), cumulative, 0,
        where=[c < 0 for c in cumulative], color="#F44336", alpha=0.2, label="Loss"
    )
    ax1.set_title("Cumulative Return")
    ax1.set_xlabel("Signal #")
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # 2. Return Distribution
    # ------------------------------------------------------------------
    ax2 = axes[1]
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r <= 0]
    ax2.hist(losses, bins=20, color="#F44336", alpha=0.7, label=f"Losses ({len(losses)})")
    ax2.hist(wins, bins=20, color="#4CAF50", alpha=0.7, label=f"Wins ({len(wins)})")
    ax2.axvline(0, color="black", linewidth=1)
    ax2.set_title("Return Distribution")
    ax2.set_xlabel("Forward Return %")
    ax2.set_ylabel("Frequency")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    safe_name = strategy_name.replace(" ", "_").replace("/", "-")
    out_path = os.path.join(_OUTPUT_DIR, f"{safe_name}_backtest.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Chart saved → {out_path}")