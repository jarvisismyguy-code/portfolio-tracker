#!/usr/bin/env python3
"""
Visual Intelligence Skill
Generates portfolio visualizations: Sankey diagrams, Sector Heatmaps, Pie charts
"""

import os
import json
import pandas as pd
from pathlib import Path

# Plotly for charts
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

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


def generate_sankey(portfolio: dict) -> str:
    """Generate Sankey diagram showing capital allocation flow"""
    if not HAS_PLOTLY:
        return ""
    
    holdings = portfolio.get("holdings", [])
    if not holdings:
        return ""
    
    # Add sectors
    for h in holdings:
        h["sector"] = SECTOR_MAP.get(h["ticker"], "Other")
    
    # Aggregate by sector
    df = pd.DataFrame(holdings)
    sector_values = df.groupby("sector")["value"].sum().reset_index()
    sector_values = sector_values.sort_values("value", ascending=False)
    
    # Build Sankey
    sectors = sector_values["sector"].tolist()
    values = sector_values["value"].tolist()
    
    # Create source/target pairs (Cash -> Sector -> Ticker)
    sources = []
    targets = []
    values_link = []
    
    # Cash -> Sector
    sector_idx_map = {s: i for i, s in enumerate(sectors)}
    
    for _, row in sector_values.iterrows():
        sources.append(0)  # Cash is index 0
        targets.append(sector_idx_map[row["sector"]] + 1)
        values_link.append(row["value"])
    
    # Sector -> Ticker
    ticker_df = df.sort_values("value", ascending=False)
    for _, row in ticker_df.iterrows():
        sources.append(sector_idx_map[row["sector"]] + 1)
        targets.append(len(sectors) + 1 + list(ticker_df["ticker"]).index(row["ticker"]))
        values_link.append(row["value"])
    
    # Labels
    labels = ["Cash"] + sectors + ticker_df["ticker"].tolist()
    
    # Colors
    colors = ["#10B981"]  # Cash is green
    colors += px.colors.qualitative.Set3[:len(sectors)]
    colors += px.colors.qualitative.Plotly[:len(ticker_df)]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values_link,
            color="rgba(150,150,150,0.4)"
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Portfolio Capital Flow - {portfolio.get('timestamp', '')}",
            font=dict(size=20)
        ),
        font=dict(size=12),
        height=600,
        width=1000
    )
    
    output_path = OUTPUT_DIR / "portfolio_sankey.png"
    fig.write_image(str(output_path), scale=2)
    print(f"[Visual] Sankey saved to {output_path}")
    return str(output_path)


def generate_sector_heatmap(portfolio: dict) -> str:
    """Generate sector allocation heatmap"""
    if not HAS_PLOTLY:
        return ""
    
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
    sector_df = sector_df.sort_values("value", ascending=False)
    
    # Create heatmap-style bar chart
    fig = go.Figure(go.Bar(
        x=sector_df["value"],
        y=sector_df["sector"],
        orientation='h',
        marker=dict(
            color=sector_df["value"],
            colorscale='Viridis',
            showscale=True
        ),
        text=[f"{v:.1f}%" for v in sector_df["pct"]],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Sector Allocation - {portfolio.get('timestamp', '')}",
            font=dict(size=20)
        ),
        xaxis_title="Value (£)",
        yaxis_title="",
        height=500,
        width=900,
        showlegend=False,
        margin=dict(l=150)
    )
    
    output_path = OUTPUT_DIR / "sector_heatmap.png"
    fig.write_image(str(output_path), scale=2)
    print(f"[Visual] Sector heatmap saved to {output_path}")
    return str(output_path)


def generate_holdings_pie(portfolio: dict) -> str:
    """Generate pie chart of holdings"""
    if not HAS_PLOTLY:
        return ""
    
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
    
    fig = go.Figure(data=[go.Pie(
        labels=tickers,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Holdings Breakdown - {portfolio.get('timestamp', '')}",
            font=dict(size=20)
        ),
        height=600,
        width=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    
    output_path = OUTPUT_DIR / "holdings_pie.png"
    fig.write_image(str(output_path), scale=2)
    print(f"[Visual] Pie chart saved to {output_path}")
    return str(output_path)


def generate_performance_bars(portfolio: dict) -> str:
    """Generate performance comparison bars"""
    if not HAS_PLOTLY:
        return ""
    
    holdings = sorted(portfolio.get("holdings", []), key=lambda x: x.get("value", 0), reverse=True)[:12]
    if not holdings:
        return ""
    
    tickers = [h["ticker"] for h in holdings]
    values = [h["value"] for h in holdings]
    pct = [h.get("pct", 0) for h in holdings]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=tickers,
        y=values,
        name="Value (£)",
        marker_color='#3B82F6',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=tickers,
        y=pct,
        name="% of Portfolio",
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#F59E0B', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Top Holdings - {portfolio.get('timestamp', '')}",
            font=dict(size=20)
        ),
        height=500,
        width=1000,
        yaxis=dict(title="Value (£)", showgrid=True),
        yaxis2=dict(title="% of Portfolio", overlaying='y', side='right'),
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(b=80)
    )
    
    output_path = OUTPUT_DIR / "holdings_bars.png"
    fig.write_image(str(output_path), scale=2)
    print(f"[Visual] Performance bars saved to {output_path}")
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
    charts = [
        ("sankey", generate_sankey),
        ("sector_heatmap", generate_sector_heatmap),
        ("holdings_pie", generate_holdings_pie),
        ("holdings_bars", generate_performance_bars)
    ]
    
    for name, func in charts:
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
        "sankey": "portfolio_sankey.png",
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
