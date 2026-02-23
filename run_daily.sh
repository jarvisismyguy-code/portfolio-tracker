#!/bin/bash
# Daily Portfolio Report Runner
# Run: python3 /home/node/.openclaw/workspace/portfolio/tracker.py

cd /home/node/.openclaw/workspace/portfolio

# Run the tracker
OUTPUT=$(python3 tracker.py 2>&1)

# Extract the report (everything after the separator)
REPORT=$(echo "$OUTPUT" | sed -n '/======$/,/======$/p' | sed '1d;$d')

# Send to Discord
if [ -n "$REPORT" ]; then
    curl -s -X POST "https://discord.com/api/v10/channels/1474082542771769354/messages" \
        -H "Authorization: Bot $(cat /home/node/.openclaw/workspace/.env 2>/dev/null | grep DISCORD_TOKEN | cut -d= -f2)" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"$REPORT\"}"
fi

echo "Report sent at $(date)"
