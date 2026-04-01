"""
Swing Trader AI Engine — main entry point.

Orchestration flow:
  1. Load all symbols from src/data/symbols_all.json
  2. Fetch daily OHLCV data for each symbol (yfinance, NSE)
  3. Run every strategy against each symbol's data
  4. Filter signals that have already been sent (deduplication)
  5. Send new signals to Telegram
  6. Persist new signals to avoid re-sending tomorrow

Run locally:
    python -m src.main

Run via GitHub Actions:
    See .github/workflows/daily.yml
"""

import sys
from src.core.fetcher import DataFetcher
from src.core.config import Config
from src.core.signal_manager import SignalManager
from src.bot.telegram_bot import TelegramBot
from src.bot.formatter import Formatter
from src.strategies.base import StrategyEngine
from src.utils.logger import logger


def run() -> int:
    """
    Execute one full scan cycle.

    Returns:
        0 on success, 1 if a fatal error occurs.
    """
    logger.info("=" * 60)
    logger.info("Swing Trader AI Engine — starting run")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Initialise components
    # ------------------------------------------------------------------
    try:
        fetcher = DataFetcher()
        signal_manager = SignalManager()
        telegram = TelegramBot()
    except EnvironmentError as exc:
        logger.error(f"Configuration error: {exc}")
        return 1

    strategies = StrategyEngine.load_all()
    logger.info(f"Loaded {len(strategies)} strategies: {[s.name() for s in strategies]}")

    # ------------------------------------------------------------------
    # Load symbol universe
    # ------------------------------------------------------------------
    try:
        symbols = Config.load_symbols()
    except (FileNotFoundError, ValueError) as exc:
        logger.error(f"Symbol list error: {exc}")
        return 1

    logger.info(f"Scanning {len(symbols)} symbols …")

    # ------------------------------------------------------------------
    # Fetch data and run strategies
    # ------------------------------------------------------------------
    all_signals = []
    period = Config.fetch_period()

    for symbol in symbols:
        df = fetcher.get(symbol, period=period)
        if df is None or df.empty:
            logger.warning(f"Skipping {symbol} — no data")
            continue

        for strat in strategies:
            try:
                signal = strat.generate(df, symbol)
                if signal:
                    logger.info(f"  ✅ Signal: {symbol} | {strat.name()}")
                    all_signals.append(signal)
            except Exception as exc:
                # Never let one bad strategy kill the whole run
                logger.error(f"Strategy error [{strat.name()}] on {symbol}: {exc}", exc_info=True)

    logger.info(f"Raw signals found: {len(all_signals)}")

    # ------------------------------------------------------------------
    # Deduplicate and send
    # ------------------------------------------------------------------
    new_signals = signal_manager.filter_new_signals(all_signals)

    if not new_signals:
        logger.info("No new signals today.")
        telegram.send_message(Formatter.no_signals())
    else:
        logger.info(f"Sending {len(new_signals)} new signal(s) …")
        for sig in new_signals:
            message = sig["format_fn"]()
            telegram.send_message(message)

    # ------------------------------------------------------------------
    # Persist sent signals
    # ------------------------------------------------------------------
    signal_manager.save_sent_signals(new_signals)

    logger.info("Run completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(run())