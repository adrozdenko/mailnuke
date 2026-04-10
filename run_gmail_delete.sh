#!/bin/bash
# Gmail Bulk Delete Runner Script

echo "Starting Gmail Bulk Delete..."
echo "Working directory: $(pwd)"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "gmail_deleter_env" ]; then
    source gmail_deleter_env/bin/activate
else
    echo "No virtual environment found. Run setup.sh first."
    exit 1
fi

# Check if credentials exist
if [ ! -f "token.pickle" ]; then
    if [ ! -f "credentials.json" ]; then
        echo "credentials.json not found!"
        echo "1. Go to https://console.cloud.google.com/"
        echo "2. Enable Gmail API"
        echo "3. Create OAuth 2.0 credentials (Desktop app)"
        echo "4. Download as credentials.json"
        echo "5. Place in this directory"
        exit 1
    fi
    echo "token.pickle not found. First run will open browser for OAuth."
fi

# Run the refactored version (recommended)
python3 main.py

echo ""
echo "Done."
