#!/usr/bin/env python3
"""
Advanced Trading212 Portfolio Tracker
- Fetches portfolio from Trading212 API
- Calculates technical indicators (RSI, MACD, SMA, EMA)
- Searches for news on each holding
- Generates daily report
"""

import os
import json
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
import tavily

# Trading212 credentials - load from environment
import os
T212_INVEST_KEY = os.getenv("T212_INVEST_KEY", "")
T212_INVEST_SECRET = os.getenv("T212_INVEST_SECRET", "")
T212_ISA_KEY = os.getenv("T212_ISA_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Discord config - load from environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")

# Your stock list from holdings.md
STOCKS = [
    # Tech
    "MSFT", "NVDA", "META", "GOOGL", "AMD", "ASML", "AVGO", "AMZN", "UBER", "ORCL", "TTD",
    # Financial
    "NWG", "BARC",
    # Consumer/Speculative
    "CELH", "NBIS", "ZENA", "ALT",
    # ETFs
    "VUSA", "VFEM", "COPX"
]

def get_t212_holdings(key_id: str, secret: str) -> list:
    """Fetch holdings from Trading212 API"""
    url = "https://api.trading212.com/v1/accounts"
    headers = {
        "Authorization": f"Basic {requests.auth.HTTPBasicAuth(key_id, secret).username}:{secret}"
    }
    
    # This is a placeholder - Trading212 API is limited
    # For now, we'll use the stock list and fetch live prices
    return []

def get_technical_indicators(ticker: str, yahoo_tickers: dict = None) -> dict:
    """Calculate RSI, MACD, SMA, EMA for a ticker"""
    try:
        # Use mapped ticker for Yahoo if available
        yf_ticker = yahoo_tickers.get(ticker, ticker) if yahoo_tickers else ticker
        stock = yf.Ticker(yf_ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 50:
            return None
            
        # Calculate indicators
        close = df['Close']
        
        # RSI (14-day)
        rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
        
        # MACD
        macd = MACD(close)
        macd_line = macd.macd().iloc[-1]
        macd_signal = macd.macd_signal().iloc[-1]
        macd_hist = macd.macd_diff().iloc[-1]
        
        # Moving Averages
        sma_20 = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
        sma_50 = SMAIndicator(close, window=50).sma_indicator().iloc[-1]
        ema_20 = EMAIndicator(close, window=20).ema_indicator().iloc[-1]
        
        # Current price
        current_price = close.iloc[-1]
        
        # Volume
        volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].tail(20).mean()
        
        # 52-week high/low
        year_high = df['High'].tail(252).max()
        year_low = df['Low'].tail(252).min()
        
        return {
            "price": round(current_price, 2),
            "rsi": round(rsi, 2),
            "macd_line": round(macd_line, 4),
            "macd_signal": round(macd_signal, 4),
            "macd_hist": round(macd_hist, 4),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "ema_20": round(ema_20, 2),
            "volume": int(volume),
            "avg_volume_20": int(avg_volume),
            "year_high": round(year_high, 2),
            "year_low": round(year_low, 2),
            "distance_from_high_pct": round((year_high - current_price) / year_high * 100, 1),
            "distance_from_low_pct": round((current_price - year_low) / year_low * 100, 1)
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def get_signal(indicators: dict) -> tuple:
    """Generate buy/sell/hold signal based on indicators"""
    rsi = indicators.get("rsi", 50)
    macd_hist = indicators.get("macd_hist", 0)
    price = indicators.get("price", 0)
    sma_20 = indicators.get("sma_20", 0)
    sma_50 = indicators.get("sma_50", 0)
    ema_20 = indicators.get("ema_20", 0)
    
    signals = []
    
    # RSI signals
    if rsi > 75:
        signals.append("RSI_OVERBOUGHT")
    elif rsi < 30:
        signals.append("RSI_OVERSOLD")
    elif rsi > 65:
        signals.append("RSI_HIGH")
    elif rsi < 40:
        signals.append("RSI_LOW")
    
    # MACD signals
    if macd_hist > 0:
        signals.append("MACD_BULLISH")
    else:
        signals.append("MACD_BEARISH")
    
    # Moving average signals
    if price > sma_20 > sma_50:
        signals.append("BULLISH_TREND")
    elif price < sma_20 < sma_50:
        signals.append("BEARISH_TREND")
    
    # Determine overall
    bullish = sum(1 for s in signals if "BULLISH" in s or "OVERSOLD" in s or "LOW" in s)
    bearish = sum(1 for s in signals if "BEARISH" in s or "OVERBOUGHT" in s or "HIGH" in s)
    
    if bullish > bearish:
        return "BULLISH", signals
    elif bearish > bullish:
        return "BEARISH", signals
    else:
        return "NEUTRAL", signals

def search_news(ticker: str, company_name: str) -> list:
    """Search for recent news on a stock using Tavily"""
    try:
        client = tavily.TavilyClient(api_key=TAVILY_API_KEY)
        query = f"{ticker} {company_name} stock news 2025"
        # Use the newer search API
        results = client.search(query=query, max_results=2)
        if isinstance(results, dict):
            return results.get('results', [])[:2]
        elif isinstance(results, list):
            return results[:2]
        return []
    except Exception as e:
        print(f"News search error for {ticker}: {e}")
        return []

def analyze_portfolio() -> dict:
    """Main analysis function"""
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "holdings": [],
        "summary": {
            "total": 0,
            "bullish": 0,
            "bearish": 0,
            "neutral": 0
        }
    }
    
    # Company names for news search - use Yahoo Finance compatible tickers
    company_names = {
        "MSFT": "Microsoft",
        "NVDA": "NVIDIA",
        "META": "Meta Facebook",
        "GOOGL": "Alphabet Google",
        "AMD": "AMD",
        "ASML": "ASML",
        "AVGO": "Broadcom",
        "AMZN": "Amazon",
        "UBER": "Uber",
        "ORCL": "Oracle",
        "TTD": "Trade Desk",
        "NWG.L": "NatWest UK",
        "BARC.L": "Barclays UK",
        "CELH": "Celsius Holdings",
        "NBIS": "Nebius",
        "ZENA": "ZenaTech",
        "ALT": "Altimmune",
        "VUSA.L": "Vanguard S&P 500",
        "VFEM.L": "Vanguard Emerging Markets",
        "COPX": "Global X Copper Miners"
    }
    
    # Yahoo Finance ticker mapping (UK stocks need .L)
    yahoo_tickers = {
        "NWG": "NWG.L",
        "BARC": "BARC.L",
        "VUSA": "VUSA.L",
        "VFEM": "VFEM.L"
    }
    
    for ticker in STOCKS:
        print(f"Analyzing {ticker}...")
        indicators = get_technical_indicators(ticker, yahoo_tickers)
        
        if not indicators:
            continue
            
        signal, signals_list = get_signal(indicators)
        
        # Get news
        company = company_names.get(ticker, ticker)
        news = search_news(ticker, company)
        
        holding = {
            "ticker": ticker,
            "company": company,
            "signal": signal,
            "signals": signals_list,
            "indicators": indicators,
            "news": news
        }
        
        report["holdings"].append(holding)
        report["summary"][signal.lower()] += 1
        report["summary"]["total"] += 1
    
    return report

def format_report(report: dict) -> str:
    """Format the report as Discord-friendly text"""
    lines = []
    lines.append(f"📊 **Portfolio Analysis** - {report['timestamp']}")
    lines.append("")
    
    # Summary
    lines.append(f"**Summary:** {report['summary']['bullish']} 🟢 Bullish | {report['summary']['neutral']} 🟡 Neutral | {report['summary']['bearish']} 🔴 Bearish")
    lines.append("")
    
    # Categorize
    bullish = [h for h in report['holdings'] if h['signal'] == "BULLISH"]
    neutral = [h for h in report['holdings'] if h['signal'] == "NEUTRAL"]
    bearish = [h for h in report['holdings'] if h['signal'] == "BEARISH"]
    
    # Overbought/Oversold alerts
    alerts = []
    watch = []
    stable = []
    
    for h in report['holdings']:
        rsi = h['indicators']['rsi']
        price = h['indicators']['price']
        
        if rsi > 75:
            alerts.append(f"🔴 **{h['ticker']}** - RSI: {rsi} (OVERBOUGHT) | ${price}")
        elif rsi < 30:
            alerts.append(f"🟢 **{h['ticker']}** - RSI: {rsi} (OVERSOLD) | ${price}")
        elif rsi > 65:
            watch.append(f"🟡 **{h['ticker']}** - RSI: {rsi} | ${price}")
        elif rsi < 40:
            watch.append(f"🟢 **{h['ticker']}** - RSI: {rsi} | ${price}")
        else:
            stable.append(f"⚪ **{h['ticker']}** - RSI: {rsi} | ${price}")
    
    if alerts:
        lines.append("**🚨 ALERTS:**")
        lines.extend(alerts)
        lines.append("")
    
    if watch:
        lines.append("**👀 WATCH:**")
        lines.extend(watch)
        lines.append("")
    
    if stable:
        lines.append("**📈 STABLE:**")
        lines.extend(stable[:10])  # Limit to avoid too long
        if len(stable) > 10:
            lines.append(f"... and {len(stable) - 10} more")
        lines.append("")
    
    # Key technical insights
    lines.append("**📊 Key Technicals:**")
    for h in report['holdings'][:5]:
        ind = h['indicators']
        lines.append(f"**{h['ticker']}**: Price ${ind['price']} | RSI {ind['rsi']} | MACD {ind['macd_hist']:.4f} | SMA20 ${ind['sma_20']} | Vol {ind['volume']/1e6:.1f}M")
    
    return "\n".join(lines)

def send_to_discord(message: str):
    """Send report to Discord channel"""
    if not DISCORD_TOKEN:
        print("No Discord token configured, skipping Discord notification")
        return
    if not DISCORD_CHANNEL_ID:
        print("No Discord channel ID configured, skipping Discord notification")
        return
    
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"content": message}
    
    try:
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code == 200:
            print("✅ Report sent to Discord")
        else:
            print(f"❌ Discord error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Discord error: {e}")

if __name__ == "__main__":
    print("Starting portfolio analysis...")
    report = analyze_portfolio()
    
    # Save JSON for debugging
    with open("/home/node/.openclaw/workspace/portfolio/daily_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    # Format and print report
    report_text = format_report(report)
    print("\n" + "="*50)
    print(report_text)
    print("="*50)
    print("\nReport saved to daily_report.json")
    
    # Send to Discord
    send_to_discord(report_text)
