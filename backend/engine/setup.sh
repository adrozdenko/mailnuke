#!/bin/bash
# Gmail Bulk Delete Tool - Quick Setup Script

echo "🚀 Gmail Bulk Delete Tool - Quick Setup"
echo "======================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.9+ and run this script again."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install click rich pydantic python-dotenv pydantic-settings
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Check if credentials exist
echo "🔐 Checking for Gmail API credentials..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  credentials.json not found!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a project and enable Gmail API"
    echo "3. Create OAuth 2.0 credentials"
    echo "4. Download as 'credentials.json' and place in this folder"
    echo "5. See USER_GUIDE.md for detailed instructions"
    echo ""
else
    echo "✅ credentials.json found!"
fi

# Create example config if it doesn't exist
if [ ! -f "delete_config.json" ]; then
    echo "⚙️  Creating example configuration..."
    cat > delete_config.json << EOF
{
  "older_than_days": 180,
  "exclude_with_attachments": true,
  "exclude_important": true,
  "exclude_starred": true,
  "dry_run": true
}
EOF
    echo "✅ Created delete_config.json with safe defaults"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Get Gmail API credentials (see USER_GUIDE.md)"
echo "2. Test with: source venv/bin/activate && python gmail_bulk_delete.py"
echo "3. Configure rules in delete_config.json"
echo "4. Run actual cleanup when ready"
echo ""
echo "📖 Read USER_GUIDE.md for complete instructions"
echo "🛡️  Remember: Tool starts in safe dry-run mode"