import json
from src.core.fetcher import DataFetcher
from src.core.config import Config
from src.core.signal_manager import SignalManager
from src.bot.telegram_bot import TelegramBot
from src.strategies.base import StrategyEngine
from src.utils.logger import logger
from src.utils.file_store import FileStore

def run():
    logger.info("Starting Swing Trader AI Engine")

    fetcher = DataFetcher()
    signal_manager = SignalManager()
    telegram = TelegramBot()

    strategies = StrategyEngine.load_all()

    symbols = Config.load_symbols()

    all_signals = []

    for symbol in symbols:
        df = fetcher.get(symbol)
        if df is None or df.empty:
            continue

        for strat in strategies:
            try:
                signal = strat.generate(df, symbol)
                if signal:
                    all_signals.append(signal)
            except Exception as e:
                logger.error(f"Strategy error {strat.name()} on {symbol}: {e}")

    new_signals = signal_manager.filter_new_signals(all_signals)

    if len(new_signals) == 0:
        telegram.send_message("📭 No signals today.")
    else:
        for sig in new_signals:
            telegram.send_message(sig.format())

    signal_manager.save_sent_signals(new_signals)
    logger.info("Run completed.")

if __name__ == "__main__":
    run()