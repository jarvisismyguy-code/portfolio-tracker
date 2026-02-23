# Saksham's Trading 212 Portfolio Tracker
# Last Updated: 2025-07-14
# Schedule: Every 2 days (Mon/Wed/Fri at 5pm UK), skip weekends
# API: Tavily only (~260 calls/month)

## Holdings by Sector/Industry

### 🖥️ Technology / Semiconductors
| Ticker | Name | Industry | Sector Benchmarks |
|--------|------|----------|-------------------|
| MSFT | Microsoft Corp | Software/Infrastructure | P/E: 25-35, Growth: 10-15% |
| NVDA | NVIDIA Corp | Semiconductors/AI | P/E: 30-60, High volatility |
| META | Meta Platforms | Social Media/AI | P/E: 20-30, Ad dependent |
| GOOGL | Alphabet Inc | Search/Cloud/AI | P/E: 20-30, Regulatory risk |
| AMD | AMD | Semiconductors | P/E: 25-50, NVDA competitor |
| ASML | ASML Holding NV | Semiconductor Equipment | Monopoly, Cyclical |
| AVGO | Broadcom Inc | Semiconductors/Software | P/E: 20-30, Dividend |
| AMZN | Amazon.com | E-commerce/Cloud | P/E: 40-60, Capital intensive |
| UBER | Uber Technologies | Ride-share/Delivery | Growth: 15-25%, Path to profit |
| ORCL | Oracle Corp | Enterprise Software | P/E: 15-25, Dividend |
| TTD | Trade Desk Inc | Ad-tech | P/E: 30-50, High growth |

### 🏦 Financial Services
| Ticker | Name | Industry | Sector Benchmarks |
|--------|------|----------|-------------------|
| NWG | NatWest Group | UK Banking | P/E: 6-10, Yield: 5-7% |
| BARC | Barclays PLC | UK Banking | P/E: 6-10, Yield: 4-6% |

### 🥤 Consumer/Speculative
| Ticker | Name | Industry | Risk Level |
|--------|------|----------|------------|
| CELH | Celsius Holdings | Energy Drinks | High growth, competition |
| NBIS | Nebius Group | AI Infrastructure | Russian-linked, geopol risk |
| ZENA | ZenaTech Inc | Drones/Microcap | Speculative, microcap |
| ALT | Altimmune Inc | Biotech/Obesity | Binary outcome, high risk |

### 📈 ETFs
| Ticker | Name | Type | Benchmark |
|--------|------|------|-----------|
| VUSA | Vanguard S&P 500 UCITS ETF | US Large Cap | S&P 500 |
| VFEM | Vanguard FTSE Emerging Markets UCITS ETF | Emerging Markets | FTSE EM |
| COPX | Global X Copper Miners ETF | Commodities/Copper | Copper cycle |

## Sector-Specific Alert Thresholds

### Technology/Semiconductors
- **RSI >75** = Overbought (higher tolerance due to momentum)
- **RSI <35** = Oversold
- **P/E >60** = Expensive (watch for correction)
- **Watch for:** Earnings misses, AI capex cuts, China restrictions

### UK Banks
- **RSI >65** = Overbought (lower volatility sector)
- **RSI <40** = Oversold
- **Yield >7%** = Potential distress signal
- **Watch for:** Rate cut impacts, credit losses, regulatory fines

### Speculative/Growth
- **RSI >80** = Extremely overbought (take profits)
- **RSI <30** = Oversold (opportunity or value trap)
- **Watch for:** Dilution, cash burn, clinical trials (ALT)

### ETFs
- **RSI >75** = Overbought
- **RSI <30** = Oversold
- **Track underlying:** S&P 500, EM markets, Copper prices

## Report Format (Mon/Wed/Fri 5pm UK)

```
📊 Portfolio Review - [DATE] 5:00 PM
Schedule: Mon/Wed/Fri | Next: [Date]

🔴 NEEDS ATTENTION:
• TICKER (Sector) - Price $X | RSI: XX | Issue: [Specific concern]

🟡 WATCH CLOSELY:
• TICKER (Sector) - Price $X | RSI: XX | Issue: [Potential issue]

🟢 STABLE:
• TICKER (Sector) - Price $X | RSI: XX | Trend: [Bullish/Neutral/Bearish]

📅 Earnings/Catalysts This Week:
• TICKER - Date - Event
```

## Report Archive
| Date | Summary | Alert Level |
|------|---------|-------------|
| - | - | - |
