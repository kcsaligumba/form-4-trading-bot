# SEC Form-4 Trading Bot

A Python-based trading bot that **monitors SEC Form-4 filings** in near real-time to detect potentially price-moving insider trades, scores them based on configurable rules, sends **Discord alerts**, and maintains a **watchlist** for follow-up.

---

## Features
- **Fast polling** of SEC EDGAR’s Form-4 feed
- Parses structured `ownership.xml` filings
- Calculates:
  - Transaction value ($)
  - % of Average Daily Dollar Volume (%ADV)
  - Insider role & title (CEO, CFO, etc.)
  - 10b5-1 plan flag
  - Trade-to-filing lag
- **Scoring system** to prioritize the most significant trades
- **Discord alerts** for high-priority trades
- **Watchlist** with automatic expiration
- Configurable thresholds via `.env`
- Backtest-ready architecture

---

## Requirements

- Python 3.10+
- VS Code (recommended)

---

## Installation
```bash
git clone https://github.com/yourusername/sec-form4-bot.git
cd sec-form4-bot

python -m venv .venv
# Activate venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

---

## Environment Variables

Required by SEC for programmatic access  
`SEC_USER_AGENT=Your Name your@email.com`

Discord webhook URL for alerts  
`DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz`

Polling interval (seconds) for new Form-4 filings  
`POLL_INTERVAL_SECONDS=60`

Minimum trade value (USD) for scoring  
`MIN_DOLLAR_VALUE=250000`

Minimum % of Average Daily Dollar Volume (ADV) for scoring  
`MIN_PCT_ADV=10`

Insider titles that receive extra scoring weight  
`PRIORITY_TITLES=ceo,cfo,chief executive,chief financial`

## Run

`python app.py`

## Testing Alerts

`python app.py --test-alert`