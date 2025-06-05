#!/bin/bash
# Stop script for S3 Browser Proxy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/s3-browser.pid"

if [[ ! -f "$PID_FILE" ]]; then
    echo "❓ PID file not found. Checking for running processes..."
    
    # Try to find by port
    PID=$(lsof -ti:3001 2>/dev/null || echo "")
    if [[ -n "$PID" ]]; then
        echo "🛑 Found process on port 3001 (PID: $PID), stopping..."
        kill "$PID"
        echo "✅ Process stopped"
    else
        echo "❓ No S3 Browser Proxy process found"
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo "🛑 Stopping S3 Browser Proxy (PID: $PID)..."
    kill "$PID"
    
    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo "⚡ Force stopping..."
        kill -9 "$PID"
    fi
    
    rm -f "$PID_FILE"
    echo "✅ S3 Browser Proxy stopped"
else
    echo "❓ Process not running (removing stale PID file)"
    rm -f "$PID_FILE"
fi
