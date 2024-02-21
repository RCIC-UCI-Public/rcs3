#!/bin/bash

# Check if running in a Docker container
if [ -f "/.dockerenv" ]; then
    echo "Running inside a Docker container."

    # Check if crond is running
    if ! pgrep crond > /dev/null; then
        echo "crond is not running. Starting crond..."
        /usr/sbin/crond start
    else
        echo "crond is already running."
    fi
else
    echo "Not running inside a Docker container. Exiting."
fi
