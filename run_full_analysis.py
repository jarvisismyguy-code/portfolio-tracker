#!/usr/bin/env python3
"""
Integrated Portfolio Analyst Runner
Combines: Technical Analysis → Fundamental Extraction → Visual Intelligence → Synthesis
Runs as daily cron at 9 AM UK
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add skills to path - use absolute paths
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILLS_DIR = SCRIPT_DIR / "skills"
PORTFOLIO_DIR = SCRIPT_DIR

# Add to path
sys.path.insert(0, str(SKILLS_DIR / "fundamental_extraction"))
sys.path.insert(0, str(SKILLS_DIR / "visual_intelligence"))
sys.path.insert(0, str(SKILLS_DIR / "synthesis_agent"))
sys.path.insert(0, str(PORTFOLIO_DIR))

# Import core tracker
from tracker import analyze_portfolio, format_report, send_to_discord

# Import skills (direct imports)
sys.path.insert(0, str(SKILLS_DIR / "fundamental_extraction"))
sys.path.insert(0, str(SKILLS_DIR / "visual_intelligence"))
sys.path.insert(0, str(SKILLS_DIR / "synthesis_agent"))

# Import fundamental extraction directly
import importlib.util
spec = importlib.util.spec_from_file_location("fundamental_extraction", SKILLS_DIR / "fundamental_extraction" / "main.py")
fundamental_extraction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fundamental_extraction)
extract_fundamentals = fundamental_extraction.extract_fundamentals

spec = importlib.util.spec_from_file_location("visual_intelligence", SKILLS_DIR / "visual_intelligence" / "main.py")
visual_intelligence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual_intelligence)
generate_all_charts = visual_intelligence.generate_all_charts
get_chart_for_discord = visual_intelligence.get_chart_for_discord

spec = importlib.util.spec_from_file_location("synthesis_agent", SKILLS_DIR / "synthesis_agent" / "main.py")
synthesis_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(synthesis_agent)
synthesize_portfolio = synthesis_agent.synthesize_portfolio
format_synthesis_message = synthesis_agent.format_synthesis_message


def find_rsi_alerts(holdings: list) -> list:
    """Find stocks with RSI extremes that need fundamental extraction"""
    alerts = []
    for h in holdings:
        rsi = h.get("indicators", {}).get("rsi", 50)
        if rsi > 65 or rsi < 35:
            alerts.append({
                "ticker": h["ticker"],
                "company": h["company"],
                "signal": h.get("signal", ""),
                "rsi": rsi
            })
    return alerts


def run_full_analysis() -> dict:
    """Run complete portfolio analysis pipeline"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "steps": {}
    }
    
    print("="*60)
    print("PORTFOLIO ANALYST - FULL ANALYSIS RUN")
    print("="*60)
    
    # Step 1: Technical Analysis
    print("\n[1/4] Running technical analysis...")
    report = analyze_portfolio()
    results["steps"]["technical"] = {
        "status": "success",
        "holdings_count": len(report.get("holdings", []))
    }
    print(f"   ✓ Analyzed {len(report.get('holdings', []))} holdings")
    
    # Step 2: Find RSI alerts and extract fundamentals
    print("\n[2/4] Checking for RSI alerts and extracting fundamentals...")
    holdings = report.get("holdings", [])
    rsi_alerts = find_rsi_alerts(holdings)
    
    fundamentals_extracted = []
    for alert in rsi_alerts:
        print(f"   → Extracting fundamentals for {alert['ticker']} (RSI: {alert['rsi']})...")
        try:
            result = extract_fundamentals(alert["ticker"], alert["company"], alert["signal"])
            if result.get("status") == "success":
                fundamentals_extracted.append(alert["ticker"])
        except Exception as e:
            print(f"   ⚠ Error: {e}")
    
    results["steps"]["fundamentals"] = {
        "status": "success",
        "alerts_found": len(rsi_alerts),
        "extracted": fundamentals_extracted
    }
    print(f"   ✓ Extracted fundamentals for {len(fundamentals_extracted)} stocks")
    
    # Step 3: Generate visualizations
    print("\n[3/4] Generating visualizations...")
    try:
        charts = generate_all_charts()
        results["steps"]["visual"] = {
            "status": "success",
            "charts": list(charts.get("charts", {}).keys())
        }
        print(f"   ✓ Generated: {', '.join(results['steps']['visual']['charts'])}")
    except Exception as e:
        print(f"   ⚠ Visual generation error: {e}")
        results["steps"]["visual"] = {"status": "error", "error": str(e)}
    
    # Step 4: Synthesis
    print("\n[4/4] Running synthesis analysis...")
    try:
        synthesis = synthesize_portfolio()
        results["steps"]["synthesis"] = {
            "status": "success",
            "average_confidence": synthesis.get("summary", {}).get("average_confidence", 0),
            "a_rated": synthesis.get("summary", {}).get("a_rated", 0),
            "sell_candidates": synthesis.get("summary", {}).get("sell_candidates", 0)
        }
        print(f"   ✓ Confidence: {synthesis.get('summary', {}).get('average_confidence', 0)}/10")
    except Exception as e:
        print(f"   ⚠ Synthesis error: {e}")
        results["steps"]["synthesis"] = {"status": "error", "error": str(e)}
    
    # Save full results
    output_file = SCRIPT_DIR / "full_analysis.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    
    return results


def send_discord_update(report: dict, synthesis: dict, charts: dict):
    """Send comprehensive update to Discord"""
    messages = []
    
    # 1. Technical Report
    tech_message = format_report(report)
    messages.append(tech_message)
    
    # 2. Synthesis Summary
    synth_message = format_synthesis_message(synthesis)
    messages.append(synth_message)
    
    # Send messages
    for msg in messages:
        send_to_discord(msg)
    
    # Send chart images
    chart_paths = [
        get_chart_for_discord("sector"),
        get_chart_for_discord("pie")
    ]
    
    for path in chart_paths:
        if path:
            # Would send image attachment here
            print(f"   [Discord] Would send chart: {path}")
    
    return messages


if __name__ == "__main__":
    print("Starting full portfolio analysis...")
    
    # Run analysis
    results = run_full_analysis()
    
    # Load generated data for Discord
    report_file = SCRIPT_DIR / "daily_report.json"
    synthesis_file = SCRIPT_DIR / "synthesis_report.json"
    
    if report_file.exists() and synthesis_file.exists():
        with open(report_file) as f:
            report = json.load(f)
        with open(synthesis_file) as f:
            synthesis = json.load(f)
        
        # Send to Discord
        print("\nSending to Discord...")
        messages = send_discord_update(report, synthesis, {})
        
        print("\n✓ Full analysis complete!")
    else:
        print("\n⚠ Report files not found - run tracker.py first")
