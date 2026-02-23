#!/usr/bin/env python3
"""
Visual Intelligence Skill
Generates portfolio visualizations using matplotlib
"""

import os
import json
import pandas as pd
from pathlib import Path

# Matplotlib for charts
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Config
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
PORTFOLIO_FILE = Path(__file__).parent.parent.parent / "portfolio_split.json"

# Sector mapping
SECTOR_MAP = {
    "MSFT": "Technology",
    "NVDA": "Technology",
    "META": "Technology",
    "GOOGL": "Technology",
    "AMD": "Technology",
    "ASML": "Technology",
    "AVGO": "Technology",
    "AMZN": "Consumer Discretionary",
    "UBER": "Technology",
    "ORCL": "Technology",
    "TTD": "Technology",
    "NWG": "Financial",
    "BARC": "Financial",
    "CELH": "Consumer Staples",
    "NBIS": "Technology",
    "ZENA": "Industrials",
    "ALT": "Healthcare",
    "VUSA": "ETF (S&P 500)",
    "VFEM": "ETF (Emerging Markets)",
    "COPX": "Commodities (Copper)"
}


def load_portfolio_data() -> dict:
    """Load portfolio from JSON file"""
    if not PORTFOLIO_FILE.exists():
        # Generate sample data for testing
        return {
            "timestamp": "2025-01-01 09:00",
            "total_value": 10000,
            "cash": 500,
            "holdings": [
                {"ticker": "MSFT", "value": 2000, "pct": 20},
                {"ticker": "NVDA", "value": 1500, "pct": 15},
                {"ticker": "META", "value": 1200, "pct": 12},
                {"ticker": "GOOGL", "value": 1000, "pct": 10},
                {"ticker": "AMZN", "value": 800, "pct": 8},
                {"ticker": "AVGO", "value": 700, "pct": 7},
                {"ticker": "AMD", "value": 600, "pct": 6},
                {"ticker": "ASML", "value": 500, "pct": 5},
                {"ticker": "ORCL", "value": 400, "pct": 4},
                {"ticker": "VUSA", "value": 800, "pct": 8},
                {"ticker": "VFEM", "value": 300, "pct": 3},
                {"ticker": "COPX", "value": 200, "pct": 2}
            ]
        }
    
    with open(PORTFOLIO_FILE) as f:
        return json.load(f)


def generate_sector_heatmap(portfolio: dict) -> str:
    """Generate sector allocation bar chart (heatmap alternative)"""
    holdings = portfolio.get("holdings", [])
    if not holdings:
        return ""
    
    # Add sectors
    for h in holdings:
        h["sector"] = SECTOR_MAP.get(h["ticker"], "Other")
    
    df = pd.DataFrame(holdings)
    sector_df = df.groupby("sector").agg({
        "value": "sum",
        "pct": "sum"
    }).reset_index()
    sector_df = sector_df.sort_values("value", ascending=True)
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.viridis([i/len(sector_df) for i in range(len(sector_df))])
    
    bars = ax.barh(sector_df["sector"], sector_df["value"], color=colors)
    
    # Add value labels
    for bar, pct in zip(bars, sector_df["pct"]):
        width = bar.get_width()
        ax.text(width + 50, bar.get_y() + bar.get_height()/2, 
                f'£{width:,.0f} ({pct:.1f}%)', 
                va='center', fontsize=10)
    
    ax.set_xlabel('Value (£)', fontsize=12)
    ax.set_title(f'Sector Allocation - {portfolio.get("timestamp", "")}', fontsize=14, fontweight='bold')
    ax.set_xlim(0, sector_df["value"].max() * 1.3)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "sector_heatmap.png"
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[Visual] Sector chart saved to {output_path}")
    return str(output_path)


def generate_holdings_pie(portfolio: dict) -> str:
    """Generate pie chart of holdings"""
    holdings = sorted(portfolio.get("holdings", []), key=lambda x: x.get("value", 0), reverse=True)
    if not holdings:
        return ""
    
    # Split into top 8 and "Others"
    top_8 = holdings[:8]
    others_value = sum(h.get("value", 0) for h in holdings[8:])
    others_pct = sum(h.get("pct", 0) for h in holdings[8:])
    
    if others_value > 0:
        top_8.append({
            "ticker": "Others",
            "value": others_value,
            "pct": others_pct
        })
    
    tickers = [h["ticker"] for h in top_8]
    values = [h["value"] for h in top_8]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = plt.cm.Set3([i/len(tickers) for i in range(len(tickers))])
    
    wedges, texts, autotexts = ax.pie(
        values, 
        labels=tickers,
        autopct='%1.1f%%',
        colors=colors,
        explode=[0.02] * len(tickers),
        startangle=90
    )
    
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    ax.set_title(f'Holdings Breakdown - {portfolio.get("timestamp", "")}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "holdings_pie.png"
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[Visual] Pie chart saved to {output_path}")
    return str(output_path)


def generate_performance_bars(portfolio: dict) -> str:
    """Generate performance comparison bars"""
    holdings = sorted(portfolio.get("holdings", []), key=lambda x: x.get("value", 0), reverse=True)[:12]
    if not holdings:
        return ""
    
    tickers = [h["ticker"] for h in holdings]
    values = [h["value"] for h in holdings]
    pct = [h.get("pct", 0) for h in holdings]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Bar chart for value
    colors = plt.cm.Blues([0.3 + 0.7*i/len(tickers) for i in range(len(tickers))])
    bars = ax1.bar(tickers, values, color=colors, alpha=0.8, label='Value (£)')
    ax1.set_xlabel('Ticker', fontsize=12)
    ax1.set_ylabel('Value (£)', fontsize=12, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'£{height:,.0f}',
                ha='center', va='bottom', fontsize=8, rotation=45)
    
    # Second y-axis for percentage
    ax2 = ax1.twinx()
    ax2.plot(tickers, pct, 'o-', color='orange', linewidth=2, markersize=8, label='% of Portfolio')
    ax2.set_ylabel('% of Portfolio', fontsize=12, color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')
    
    plt.title(f'Top Holdings - {portfolio.get("timestamp", "")}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "holdings_bars.png"
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[Visual] Bar chart saved to {output_path}")
    return str(output_path)


def generate_all_charts() -> dict:
    """Generate all visualizations"""
    print("[Visual] Loading portfolio data...")
    portfolio = load_portfolio_data()
    
    results = {
        "portfolio": portfolio,
        "charts": {}
    }
    
    # Generate all charts
    chart_funcs = [
        ("sector_heatmap", generate_sector_heatmap),
        ("holdings_pie", generate_holdings_pie),
        ("holdings_bars", generate_performance_bars)
    ]
    
    for name, func in chart_funcs:
        try:
            path = func(portfolio)
            if path:
                results["charts"][name] = path
        except Exception as e:
            print(f"[Visual] Error generating {name}: {e}")
            results["charts"][name] = None
    
    return results


def get_chart_for_discord(chart_type: str = "sector_heatmap") -> str:
    """Get specific chart path for Discord"""
    chart_map = {
        "sankey": "sector_heatmap.png",
        "sector": "sector_heatmap.png",
        "pie": "holdings_pie.png",
        "bars": "holdings_bars.png"
    }
    
    filename = chart_map.get(chart_type, chart_type + ".png")
    path = OUTPUT_DIR / filename
    
    if path.exists():
        return str(path)
    return ""


if __name__ == "__main__":
    results = generate_all_charts()
    print(f"\n[Visual] Generated charts: {list(results['charts'].keys())}")
