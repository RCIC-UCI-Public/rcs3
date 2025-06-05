#!/bin/bash
# Start script for S3 Browser Proxy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/s3-browser.pid"
LOG_FILE="$SCRIPT_DIR/s3-browser.log"

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "❌ S3 Browser Proxy is already running (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Check credentials
if [[ ! -f "config/credentials.json" ]]; then
    echo "❌ AWS credentials not found. Please edit config/credentials.json with your AWS credentials."
    exit 1
fi

echo "🚀 Starting S3 Browser Proxy..."
echo "   Access at: http://localhost:3001"
echo "   Logs: $LOG_FILE"
echo "   PID file: $PID_FILE"

# Start in background
nohup node server.js > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo $SERVER_PID > "$PID_FILE"

# Wait a moment and verify it started
sleep 2
if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "✅ S3 Browser Proxy started successfully (PID: $SERVER_PID)"
    echo ""
    echo "Management commands:"
    echo "  ./stop-service.sh     - Stop the service"
    echo "  ./status-service.sh   - Check service status"
    echo "  ./logs-service.sh     - View logs"
else
    echo "❌ Failed to start S3 Browser Proxy"
    echo "Check logs: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
