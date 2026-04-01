# 📈 AI Swing Trader — NSE Scanner

An automated swing-trading signal engine for NSE (India) stocks.
Runs daily via GitHub Actions, scans a configurable symbol universe with 8
technical strategies, and delivers buy signals to a Telegram channel.

---

## 🗂 Project Structure

```
ai-swing-trader/
├── src/
│   ├── main.py                  # Entry point
│   ├── core/
│   │   ├── config.py            # Env-var configuration
│   │   ├── fetcher.py           # yfinance data fetcher
│   │   ├── ohlcv.py             # OHLCV column accessors
│   │   └── signal_manager.py    # Deduplication & persistence
│   ├── bot/
│   │   ├── telegram_bot.py      # Telegram sender (with retry)
│   │   └── formatter.py         # Message formatting
│   ├── strategies/
│   │   ├── base.py              # BaseStrategy + StrategyEngine
│   │   ├── sma_strategy.py      # SMA 20/50/200 pullback
│   │   ├── knoxville.py         # Knoxville Divergence (RSI + momentum)
│   │   ├── v20.py               # V20 momentum breakout
│   │   ├── rhs.py               # Reverse Head & Shoulders
│   │   ├── cwh.py               # Cup With Handle
│   │   ├── v10.py               # V10 sharp reversal
│   │   ├── lifetime_high.py     # 30 %+ discount from ATH
│   │   └── three_x_three_years.py  # 3× recovery setup
│   ├── data/
│   │   └── symbols_all.json     # Symbol universe (edit freely)
│   └── utils/
│       ├── logger.py            # Rotating file + console logger
│       ├── file_store.py        # Atomic JSON persistence
│       └── patterns.py          # RHS / CWH / V10 pattern detectors
├── backtest/
│   ├── engine/
│   │   ├── backtester.py        # Walk-forward engine
│   │   ├── metrics.py           # Win rate, profit factor, expectancy
│   │   └── plot_results.py      # Equity curve + return distribution
│   └── run_backtest.py          # CLI backtest runner
└── .github/workflows/daily.yml  # Scheduled GitHub Action (Mon–Fri 7 PM IST)
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ai-swing-trader.git
cd ai-swing-trader
pip install -r requirements.txt
```

### 2. Configure Telegram

1. Create a bot via [@BotFather](https://t.me/BotFather) and copy the token.
2. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot).
3. Export the env vars locally or add them as GitHub Secrets:

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

### 3. Customise the Symbol Universe

Edit `src/data/symbols_all.json` — a plain JSON array of NSE tickers (no `.NS` suffix):

```json
["RELIANCE", "TCS", "INFY", "HDFCBANK"]
```

### 4. Run Locally

```bash
python -m src.main
```

---

## 🔁 GitHub Actions (Automated Daily Run)

Add these two **Repository Secrets** (Settings → Secrets → Actions):

| Secret name       | Value                        |
|-------------------|------------------------------|
| `TG_TOKEN`        | Your Telegram bot token      |
| `TG_CHAT_ID`      | Your Telegram chat/channel ID |

The workflow runs automatically at **7:00 PM IST, Monday–Friday**.
You can also trigger it manually from the Actions tab.

---

## 📊 Backtesting

Run a walk-forward backtest on any strategy:

```bash
# Default: SMA strategy on RELIANCE, 3y history, 10-bar forward window
python -m backtest.run_backtest

# Custom
python -m backtest.run_backtest --strategy knoxville --symbol INFY --period 3y --forward 15
```

**Available strategy keys:** `sma`, `knoxville`, `v20`, `rhs`, `cwh`, `v10`, `lifetime`, `threex`

Charts are saved to `backtest/output/`.

---

## 📐 Strategies

| Strategy | Signal Condition | Target | Stoploss |
|----------|-----------------|--------|----------|
| SMA 20/50/200 | Pullback to SMA20 in uptrend | MA reversal | 3% below day's low |
| Knoxville Divergence | RSI < 40 + positive momentum | Trend continuation | Recent swing low |
| V20 | 5-day unbroken rally ≥ 20% | +10% continuation | 5-day low |
| Reverse H&S | 3-trough pattern + neckline break | 1.4× neckline | 3% below entry |
| Cup With Handle | U-shape cup + shallow handle breakout | +35% | Below handle low |
| V10 | ≥10% drop fully recovered | +10% | 5-bar swing low |
| Lifetime High | ≥30% below ATH | ATH | −10% |
| 3× in 3 Years | ≤33% of 3-year high | 3-year high | −15% |

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**.
It does not constitute financial advice.  Past backtested performance does not
guarantee future results.  Always do your own research before investing.