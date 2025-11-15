#!/bin/bash
# Quick start script for Word Recite

cd "$(dirname "$0")"

# Check if dependencies are installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Run the application
echo "Starting Word Recite..."
echo "Note: The application window should appear shortly."
echo "If you don't see it, check if it's in the background or minimized."
python3 main.py &

# Store the PID
PID=$!
echo "Application started with PID: $PID"
echo "To stop: kill $PID"
