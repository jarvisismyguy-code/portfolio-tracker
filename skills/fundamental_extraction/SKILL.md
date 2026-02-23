# Fundamental Extraction Skill

## Description
When a stock is flagged technically (RSI >65 or <35), trigger a web search to find the latest Investor Relations PDF (10-Q/10-K). Extract Revenue, COGS, Gross Profit, and EPS Guidance into a structured `fundamentals.json`.

## Trigger Conditions
- RSI_OVERBOUGHT (RSI > 75)
- RSI_OVERSOLD (RSI < 30)
- RSI_HIGH (RSI > 65)
- RSI_LOW (RSI < 35)

## Inputs
- `ticker`: Stock symbol (e.g., "NVDA")
- `company_name`: Full company name
- `signal`: Technical signal that triggered

## Outputs
- `fundamentals/{ticker}.json`: Extracted financial data
- Returns extracted metrics: Revenue, COGS, Gross Profit, Operating Income, Net Income, EPS, EPS Guidance, P/E ratio

## Dependencies
- tavily (web search)
- requests (download PDFs)
- pdfplumber or PyPDF2 (PDF parsing)

## Usage
```python
from skills.fundamental_extraction.main import extract_fundamentals
result = extract_fundamentals("NVDA", "NVIDIA Corporation", "RSI_OVERSOLD")
```

## Timeout
60 seconds per stock (Tavily search + PDF download + parsing)
