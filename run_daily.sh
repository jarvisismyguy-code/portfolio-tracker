#!/bin/bash
# Full Portfolio Analyst Runner
# Runs: Technical → Fundamentals → Visual → Synthesis
# Cron: 9 AM UK weekdays

cd /home/node/.openclaw/workspace/portfolio

echo "========================================"
echo "PORTFOLIO ANALYST - $(date)"
echo "========================================"

# Set environment (load from workspace .env)
export T212_INVEST_KEY="39131057ZfUhoXDuIKAwbPAWqQIaWpDwcfzUW"
export T212_INVEST_SECRET="KpHkJQ3jFkCvDYqGpVN1KDw5Ru1TbIUKlOVwf04x4NE"
export T212_ISA_KEY="39097304ZuMPfRIoZdRuQWVYAwpDwfqpKbZfY"
export TAVILY_API_KEY="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"
export DISCORD_CHANNEL_ID="1475601423122039028"

# Run full analysis
python3 run_full_analysis.py

# Check results
if [ -f "portfolio/daily_report.json" ]; then
    echo "✓ Technical analysis complete"
fi

if [ -f "fundamentals/"*.json 2>/dev/null ]; then
    echo "✓ Fundamentals extracted"
fi

if [ -f "outputs/"*.png 2>/dev/null ]; then
    echo "✓ Visualizations generated"
fi

if [ -f "portfolio/synthesis_report.json" ]; then
    echo "✓ Synthesis complete"
fi

echo "========================================"
echo "DONE - $(date)"
echo "========================================"
