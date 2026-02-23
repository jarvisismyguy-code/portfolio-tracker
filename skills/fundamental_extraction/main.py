#!/usr/bin/env python3
"""
Fundamental Extraction Skill
Triggered when stocks are flagged technically (RSI extremes)
Finds latest 10-Q/10-K PDF and extracts key metrics
"""

import os
import json
import re
import tempfile
import requests
from datetime import datetime
from pathlib import Path

# Try pdfplumber first, fall back to PyPDF2
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

import tavily

# Config
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
OUTPUT_DIR = Path(__file__).parent.parent.parent / "fundamentals"
OUTPUT_DIR.mkdir(exist_ok=True)

# SEC EDGAR as fallback source
SEC_BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"


def search_ir_pdf(ticker: str, company_name: str) -> dict:
    """Search for Investor Relations PDF using Tavily"""
    if not TAVILY_API_KEY:
        return {"error": "No Tavily API key"}
    
    try:
        client = tavily.TavilyClient(api_key=TAVILY_API_KEY)
        
        # Search for 10-K first, then 10-Q
        queries = [
            f"{ticker} {company_name} investor relations 2024 10-K annual report PDF",
            f"{ticker} {company_name} 2024 Q3 Q4 earnings report PDF"
        ]
        
        for query in queries:
            results = client.search(query=query, max_results=5)
            if isinstance(results, dict):
                results = results.get('results', [])
            
            # Look for PDF links
            for r in results:
                url = r.get('url', '')
                title = r.get('title', '')
                
                # Check if it's a PDF or IR page
                if '.pdf' in url.lower() or 'investor' in url.lower():
                    return {
                        "url": url,
                        "title": title,
                        "source": "tavily"
                    }
        
        # Fallback: try SEC EDGAR
        return {
            "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-K&count=10",
            "title": f"SEC EDGAR - {ticker}",
            "source": "sec"
        }
        
    except Exception as e:
        return {"error": str(e)}


def extract_text_from_pdf(url: str) -> str:
    """Download and extract text from PDF"""
    text = ""
    
    try:
        # Download PDF
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=30)
        
        if resp.status_code != 200:
            return ""
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(resp.content)
            temp_path = f.name
        
        # Extract text
        if HAS_PDFPLUMBER:
            with pdfplumber.open(temp_path) as pdf:
                for page in pdf.pages[:20]:  # First 20 pages (usually covers)
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif HAS_PYPDF2:
            reader = PdfReader(temp_path)
            for page in reader.pages[:20]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
    
    return text


def parse_financials(text: str, ticker: str) -> dict:
    """Parse key financial metrics from extracted text"""
    metrics = {}
    
    # Clean text
    text = text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')
    
    # Revenue patterns (look for billions/millions)
    revenue_patterns = [
        r'(?:Total\s+)?Revenue[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Net\s+Sales[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Product\s+Revenue[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Service\s+Revenue[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
    ]
    
    for pattern in revenue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            # Normalize to billions
            if val < 100:  # Probably already in billions
                metrics['revenue_billions'] = val
            else:  # Probably in millions
                metrics['revenue_billions'] = val / 1000
            break
    
    # COGS / Cost of Revenue
    cogs_patterns = [
        r'Cost\s+of\s+(?:Revenue|Products|Sales)[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Cost\s+of\s+Revenue[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
    ]
    
    for pattern in cogs_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if val < 100:
                metrics['cogs_billions'] = val
            else:
                metrics['cogs_billions'] = val / 1000
            break
    
    # Gross Profit
    if 'revenue_billions' in metrics and 'cogs_billions' in metrics:
        metrics['gross_profit_billions'] = metrics['revenue_billions'] - metrics['cogs_billions']
        if metrics['revenue_billions'] > 0:
            metrics['gross_margin_pct'] = round(
                metrics['gross_profit_billions'] / metrics['revenue_billions'] * 100, 1
            )
    
    # Operating Income
    op_income_patterns = [
        r'Operating\s+Income[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Operating\s+Profit[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
    ]
    
    for pattern in op_income_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            metrics['operating_income_billions'] = val if val < 100 else val / 1000
            break
    
    # Net Income
    net_income_patterns = [
        r'Net\s+Income[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
        r'Net\s+(?:Earnings|Profit)[:\s]+[\$]?([\d]+\.?[\d]*)\s*(?:billion|B)',
    ]
    
    for pattern in net_income_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            metrics['net_income_billions'] = val if val < 100 else val / 1000
            break
    
    # EPS
    eps_patterns = [
        r'(?:Diluted\s+)?EPS[:\s]+[\$]?([\d]+\.?[\d]*)',
        r'Earnings\s+per\s+Share[:\s]+[\$]?([\d]+\.?[\d]*)',
    ]
    
    for pattern in eps_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metrics['eps'] = float(match.group(1))
            break
    
    # EPS Guidance / Forward EPS
    guidance_patterns = [
        r'(?:FY|Full\s+Year)\s*(?:2024|2025)?\s*(?:EPS|earnings).*?(?:guidance|outlook|expected)[:\s]+[\$]?([\d]+\.?[\d]*)',
        r'(?:Forward|Estimated)\s+EPS[:\s]+[\$]?([\d]+\.?[\d]*)',
        r'202[45]\s*(?:EPS|earnings).*?guidance[:\s]+[\$]?([\d]+\.?[\d]*)',
    ]
    
    for pattern in guidance_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metrics['eps_guidance'] = float(match.group(1))
            break
    
    return metrics


def extract_fundamentals(ticker: str, company_name: str, signal: str = "") -> dict:
    """Main function to extract fundamentals for a ticker"""
    result = {
        "ticker": ticker,
        "company": company_name,
        "signal_trigger": signal,
        "timestamp": datetime.now().isoformat(),
        "data": {},
        "status": "pending"
    }
    
    # Step 1: Search for IR PDF
    print(f"[Fundamentals] Searching for {ticker} financial data...")
    search_result = search_ir_pdf(ticker, company_name)
    
    if "error" in search_result:
        result["status"] = "error"
        result["error"] = search_result["error"]
        return result
    
    result["source_url"] = search_result.get("url")
    result["source"] = search_result.get("source")
    
    # Step 2: If PDF found, extract text
    if search_result.get("source") == "tavily" and ".pdf" in search_result.get("url", "").lower():
        print(f"[Fundamentals] Downloading PDF from {search_result['url']}")
        text = extract_text_from_pdf(search_result["url"])
        
        if text:
            # Step 3: Parse financials
            metrics = parse_financials(text, ticker)
            result["data"] = metrics
            result["status"] = "success" if metrics else "parsed_empty"
            print(f"[Fundamentals] Extracted: {metrics}")
        else:
            result["status"] = "pdf_extract_failed"
    else:
        # SEC page - mark for manual review
        result["status"] = "sec_fallback"
    
    # Save to file
    output_file = OUTPUT_DIR / f"{ticker}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Fundamentals] Saved to {output_file}")
    return result


def batch_extract(tickers: list) -> dict:
    """Extract fundamentals for multiple tickers"""
    results = {}
    for ticker, company_name, signal in tickers:
        results[ticker] = extract_fundamentals(ticker, company_name, signal)
    return results


if __name__ == "__main__":
    # Test
    test_cases = [
        ("NVDA", "NVIDIA Corporation", "RSI_OVERSOLD"),
        ("MSFT", "Microsoft Corporation", "RSI_OVERBOUGHT"),
    ]
    
    for ticker, company, signal in test_cases:
        result = extract_fundamentals(ticker, company, signal)
        print(json.dumps(result, indent=2))
        print("---")
