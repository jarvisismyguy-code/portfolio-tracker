# Trading212 Portfolio Tracker

Discord bot that delivers daily portfolio analysis with technical indicators, news, and alerts.

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install requests pandas yfinance ta tavily python-dotenv
   ```

3. Copy `config.example.env` to `.env` and fill in your credentials:
   ```bash
   cp config.example.env .env
   ```

4. Run the tracker:
   ```bash
   python tracker.py
   ```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `T212_INVEST_KEY` | Trading212 Invest account API key |
| `T212_INVEST_SECRET` | Trading212 Invest account API secret |
| `T212_ISA_KEY` | Trading212 ISA account API key |
| `TAVILY_API_KEY` | Tavily API key for news search |
| `DISCORD_TOKEN` | Discord bot token |
| `DISCORD_CHANNEL_ID` | Discord channel for updates |

## Features

- **Technical Analysis**: RSI, MACD, SMA, EMA indicators
- **Signal Generation**: Bullish/Bearish/Neutral based on composite indicators
- **News Aggregation**: Real-time news via Tavily
- **Discord Integration**: Automated daily reports
- **Alert System**: Overbought/Oversold RSI alerts

## Schedule

Runs daily at 9 AM UK via OpenClaw cron.

## License

MIT
