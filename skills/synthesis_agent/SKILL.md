# Synthesis Agent Skill

## Description
The "brain" of the financial analyst. Takes (A) Technical Flags, (B) Fundamental JSON data, and (C) Market News. Outputs a "Confidence Score" (1-10) for each holding and suggests rebalance actions if score < 5.

## Trigger Conditions
- After technical analysis + fundamental extraction complete
- Daily synthesis at 9 AM alongside report

## Inputs
- `daily_report.json`: Technical indicators and signals
- `fundamentals/*.json`: Extracted fundamental data
- News from Tavily searches

## Outputs
- `synthesis_report.json`: Confidence scores and recommendations
- Discord message with summary

## Confidence Score Algorithm (1-10)

### Technical Score (40% weight)
- RSI in sweet spot (40-60): +2
- RSI oversold (<30): +3 (potential upside)
- RSI overbought (>75): -3 (risk)
- MACD bullish: +1
- MACD bearish: -1
- Price above SMA 20/50: +1 each

### Fundamental Score (35% weight)
- Revenue growth YoY: +2
- Gross margin >50%: +1
- Positive EPS guidance: +2
- P/E in healthy range (15-30): +1
- Negative guidance: -3

### Sentiment Score (25% weight)
- Positive news: +2
- Negative news: -2
- Neutral: 0

### Score Thresholds
- **8-10**: Strong Buy / Hold - "A+ Portfolio"
- **6-7**: Buy / Hold - "Solid"
- **5**: Hold - "Watch List"
- **4-3**: Consider Reducing - "Cautious"
- **1-2**: Strong Sell - "High Risk"

## Rebalance Logic
If confidence < 5:
- Generate specific action: SELL X%, ADD TO WATCH, HEDGE
- Show risk factors

## Usage
```python
from skills.synthesis_agent.main import synthesize_portfolio
report = synthesize_portfolio()
```
