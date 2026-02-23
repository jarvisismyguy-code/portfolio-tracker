#!/usr/bin/env python3
"""
Synthesis Agent Skill
Combines Technical + Fundamental + Sentiment into Confidence Scores
Suggests rebalance actions for low-confidence holdings
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Import from parent modules
TRACKER_DIR = Path(__file__).parent.parent.parent
REPORT_FILE = TRACKER_DIR / "portfolio" / "daily_report.json"
FUNDAMENTALS_DIR = TRACKER_DIR / "fundamentals"
OUTPUT_FILE = TRACKER_DIR / "portfolio" / "synthesis_report.json"


# Weights for confidence scoring
WEIGHTS = {
    "technical": 0.40,
    "fundamental": 0.35,
    "sentiment": 0.25
}


def load_daily_report() -> dict:
    """Load technical analysis report"""
    if REPORT_FILE.exists():
        with open(REPORT_FILE) as f:
            return json.load(f)
    return {}


def load_fundamentals(ticker: str) -> dict:
    """Load fundamentals JSON for a ticker"""
    fund_file = FUNDAMENTALS_DIR / f"{ticker}.json"
    if fund_file.exists():
        with open(fund_file) as f:
            return json.load(f)
    return {}


def calculate_technical_score(indicators: dict, signals: list) -> tuple:
    """Calculate technical component of confidence (0-10)"""
    score = 5  # Start neutral
    breakdown = []
    
    rsi = indicators.get("rsi", 50)
    macd_hist = indicators.get("macd_hist", 0)
    price = indicators.get("price", 0)
    sma_20 = indicators.get("sma_20", 0)
    sma_50 = indicators.get("sma_50", 0)
    
    # RSI scoring
    if 40 <= rsi <= 60:
        score += 1.5
        breakdown.append(f"RSI sweet spot (50): +1.5")
    elif rsi < 30:
        score += 3  # Oversold = potential upside
        breakdown.append(f"RSI oversold ({rsi}): +3")
    elif rsi < 40:
        score += 1.5
        breakdown.append(f"RSI low ({rsi}): +1.5")
    elif rsi > 75:
        score -= 3
        breakdown.append(f"RSI overbought ({rsi}): -3")
    elif rsi > 65:
        score -= 1.5
        breakdown.append(f"RSI high ({rsi}): -1.5")
    
    # MACD scoring
    if macd_hist > 0:
        score += 1
        breakdown.append(f"MACD bullish: +1")
    else:
        score -= 1
        breakdown.append(f"MACD bearish: -1")
    
    # Moving average scoring
    if price > sma_20 > sma_50:
        score += 2
        breakdown.append(f"Uptrend (price>MA20>MA50): +2")
    elif price < sma_20 < sma_50:
        score -= 2
        breakdown.append(f"Downtrend: -2")
    elif price > sma_20:
        score += 1
        breakdown.append(f"Above SMA20: +1")
    
    # Signal-based adjustments
    for sig in signals:
        if "OVERBOUGHT" in sig:
            score -= 1.5
            breakdown.append(f"{sig}: -1.5")
        elif "OVERSOLD" in sig:
            score += 1
            breakdown.append(f"{sig}: +1")
        elif "BULLISH" in sig and sig != "MACD_BULLISH":
            score += 0.5
            breakdown.append(f"{sig}: +0.5")
        elif "BEARISH" in sig and sig != "MACD_BEARISH":
            score -= 0.5
            breakdown.append(f"{sig}: -0.5")
    
    # Normalize to 0-10
    score = max(0, min(10, score))
    return round(score, 1), breakdown


def calculate_fundamental_score(fundamentals: dict) -> tuple:
    """Calculate fundamental component of confidence (0-10)"""
    score = 5  # Start neutral
    breakdown = []
    
    data = fundamentals.get("data", {})
    if not data:
        return 5.0, ["No fundamentals available: 5"]
    
    # Revenue check
    revenue = data.get("revenue_billions", 0)
    if revenue > 50:  # Large cap
        score += 1.5
        breakdown.append(f"Large cap revenue (${revenue}B): +1.5")
    elif revenue > 10:
        score += 1
        breakdown.append(f"Mid cap revenue (${revenue}B): +1")
    
    # Gross margin
    gross_margin = data.get("gross_margin_pct", 0)
    if gross_margin > 60:
        score += 2
        breakdown.append(f"High margin ({gross_margin}%): +2")
    elif gross_margin > 50:
        score += 1
        breakdown.append(f"Good margin ({gross_margin}%): +1")
    elif gross_margin < 20:
        score -= 2
        breakdown.append(f"Low margin ({gross_margin}%): -2")
    
    # EPS guidance
    eps_guidance = data.get("eps_guidance")
    eps = data.get("eps", 0)
    
    if eps_guidance and eps:
        if eps_guidance > eps:
            score += 2.5
            breakdown.append(f"Raising guidance ({eps}->{eps_guidance}): +2.5")
        elif eps_guidance < eps * 0.9:
            score -= 3
            breakdown.append(f"Guidance cut: -3")
        else:
            score += 1
            breakdown.append(f"Stable guidance: +1")
    
    # EPS positive
    if eps and eps > 0:
        score += 1
        breakdown.append(f"Positive EPS ({eps}): +1")
    
    # Operating income positive
    op_income = data.get("operating_income_billions", 0)
    if op_income > 0:
        score += 1
        breakdown.append(f"Operating profit: +1")
    
    # Normalize
    score = max(0, min(10, score))
    return round(score, 1), breakdown


def calculate_sentiment_score(news: list) -> tuple:
    """Calculate sentiment component of confidence (0-10)"""
    score = 5  # Start neutral
    breakdown = []
    
    if not news:
        return 5.0, ["No news: 5"]
    
    positive_keywords = ["beat", "raise", "growth", "bullish", "upgrade", "profit", "soar", "rally", "record"]
    negative_keywords = ["miss", "cut", "downgrade", "loss", "fear", "crash", "plunge", "warning", "layoff"]
    
    positive_count = 0
    negative_count = 0
    
    for article in news:
        title = (article.get("title", "") + " " + article.get("content", "")).lower()
        
        for kw in positive_keywords:
            if kw in title:
                positive_count += 1
                break
        for kw in negative_keywords:
            if kw in title:
                negative_count += 1
                break
    
    if positive_count > negative_count:
        score += min(3, positive_count - negative_count)
        breakdown.append(f"Positive news ({positive_count}): +{min(3, positive_count - negative_count)}")
    elif negative_count > positive_count:
        score -= min(3, negative_count - positive_count)
        breakdown.append(f"Negative news ({negative_count}): -{min(3, negative_count - positive_count)}")
    
    score = max(0, min(10, score))
    return round(score, 1), breakdown


def calculate_confidence_score(holding: dict, fundamentals: dict) -> dict:
    """Calculate overall confidence score for a holding"""
    # Technical
    tech_score, tech_breakdown = calculate_technical_score(
        holding.get("indicators", {}),
        holding.get("signals", [])
    )
    
    # Fundamental
    fund_score, fund_breakdown = calculate_fundamental_score(fundamentals)
    
    # Sentiment
    sent_score, sent_breakdown = calculate_sentiment_score(holding.get("news", []))
    
    # Weighted total
    weighted = (
        tech_score * WEIGHTS["technical"] +
        fund_score * WEIGHTS["fundamental"] +
        sent_score * WEIGHTS["sentiment"]
    )
    
    confidence = round(weighted, 1)
    
    # Determine rating
    if confidence >= 8:
        rating = "A+"
        action = "HOLD"
        reason = "Strong buy/hold signal"
    elif confidence >= 7:
        rating = "A"
        action = "HOLD"
        reason = "Solid position"
    elif confidence >= 6:
        rating = "B+"
        action = "HOLD"
        reason = "Positive, monitor"
    elif confidence >= 5:
        rating = "B"
        action = "WATCH"
        reason = "Neutral, watch for changes"
    elif confidence >= 4:
        rating = "C"
        action = "CONSIDER REDUCING"
        reason = "Caution advised"
    elif confidence >= 3:
        rating = "D"
        action = "REDUCE"
        reason = "Higher risk"
    else:
        rating = "F"
        action = "SELL"
        reason = "High risk - consider exit"
    
    # Special rebalance logic for low confidence
    if confidence < 5:
        risk_factors = []
        
        rsi = holding.get("indicators", {}).get("rsi", 50)
        if rsi > 70:
            risk_factors.append("RSI overbought")
        if rsi < 35:
            risk_factors.append("RSI oversold - potential trap")
        
        if fund_score < 4:
            risk_factors.append("Weak fundamentals")
        
        if sent_score < 4:
            risk_factors.append("Negative sentiment")
        
        suggestion = f"Consider reducing {holding.get('ticker')} position. Risk factors: {', '.join(risk_factors)}"
    else:
        suggestion = f"Hold {holding.get('ticker')} - {reason}"
    
    return {
        "ticker": holding.get("ticker"),
        "company": holding.get("company"),
        "confidence": confidence,
        "rating": rating,
        "action": action,
        "reason": reason,
        "suggestion": suggestion,
        "breakdown": {
            "technical": {"score": tech_score, "details": tech_breakdown},
            "fundamental": {"score": fund_score, "details": fund_breakdown},
            "sentiment": {"score": sent_score, "details": sent_breakdown}
        }
    }


def synthesize_portfolio() -> dict:
    """Main synthesis function - analyze all holdings"""
    print("[Synthesis] Loading portfolio data...")
    
    # Load technical report
    report = load_daily_report()
    holdings = report.get("holdings", [])
    
    if not holdings:
        # Return sample for testing
        holdings = [
            {
                "ticker": "NVDA",
                "company": "NVIDIA",
                "signals": ["RSI_OVERSOLD", "MACD_BULLISH"],
                "indicators": {"rsi": 28, "macd_hist": 0.5, "price": 500, "sma_20": 480, "sma_50": 450},
                "news": [{"title": "NVDA beats earnings", "content": "Strong AI demand"}]
            },
            {
                "ticker": "MSFT",
                "company": "Microsoft",
                "signals": ["RSI_HIGH", "MACD_BEARISH"],
                "indicators": {"rsi": 72, "macd_hist": -0.2, "price": 400, "sma_20": 390, "sma_50": 380},
                "news": [{"title": "MSFT raises guidance", "content": "Cloud growth strong"}]
            }
        ]
    
    # Analyze each holding
    results = []
    for holding in holdings:
        ticker = holding.get("ticker")
        
        # Load fundamentals
        fundamentals = load_fundamentals(ticker)
        
        # Calculate confidence
        analysis = calculate_confidence_score(holding, fundamentals)
        results.append(analysis)
    
    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Generate summary
    a_rated = [r for r in results if r["confidence"] >= 7]
    watch_list = [r for r in results if 5 <= r["confidence"] < 7]
    sell_candidates = [r for r in results if r["confidence"] < 5]
    
    synthesis = {
        "timestamp": datetime.now().isoformat(),
        "total_holdings": len(results),
        "summary": {
            "a_rated": len(a_rated),
            "watch_list": len(watch_list),
            "sell_candidates": len(sell_candidates),
            "average_confidence": round(sum(r["confidence"] for r in results) / len(results), 1) if results else 0
        },
        "a_rated": a_rated,
        "watch_list": watch_list,
        "sell_candidates": sell_candidates,
        "all_holdings": results
    }
    
    # Save report
    with open(OUTPUT_FILE, "w") as f:
        json.dump(synthesis, f, indent=2)
    
    print(f"[Synthesis] Saved to {OUTPUT_FILE}")
    print(f"[Synthesis] A-rated: {len(a_rated)}, Watch: {len(watch_list)}, Sell: {len(sell_candidates)}")
    
    return synthesis


def format_synthesis_message(synthesis: dict) -> str:
    """Format synthesis as Discord message"""
    lines = []
    
    lines.append("🎯 **PORTFOLIO CONFIDENCE ANALYSIS**")
    lines.append("")
    
    summary = synthesis["summary"]
    lines.append(f"**Overall Score:** {summary['average_confidence']}/10")
    lines.append(f"🟢 A-Rated: {summary['a_rated']} | 🟡 Watch: {summary['watch_list']} | 🔴 Sell: {summary['sell_candidates']}")
    lines.append("")
    
    # A-rated
    if synthesis["a_rated"]:
        lines.append("**🟢 STRONG HOLDS:**")
        for h in synthesis["a_rated"][:5]:
            lines.append(f"• **{h['ticker']}** ({h['rating']}) - Confidence: {h['confidence']}/10")
        lines.append("")
    
    # Sell candidates
    if synthesis["sell_candidates"]:
        lines.append("**🔴 SELL CONSIDERATION:**")
        for h in synthesis["sell_candidates"]:
            lines.append(f"• **{h['ticker']}** ({h['rating']}) - {h['suggestion']}")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    report = synthesize_portfolio()
    print(json.dumps(report, indent=2))
    print("\n" + "="*50)
    print(format_synthesis_message(report))
