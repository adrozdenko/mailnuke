@echo off
REM Gmail Bulk Delete Tool - Windows Setup Script

echo 🚀 Gmail Bulk Delete Tool - Quick Setup
echo =======================================

REM Check Python version
echo 📋 Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed.
    echo Please install Python 3.9+ from https://python.org and run this script again.
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install click rich pydantic python-dotenv pydantic-settings
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

REM Check if credentials exist
echo 🔐 Checking for Gmail API credentials...
if not exist "credentials.json" (
    echo ⚠️  credentials.json not found!
    echo.
    echo 📋 Next Steps:
    echo 1. Go to: https://console.cloud.google.com/
    echo 2. Create a project and enable Gmail API
    echo 3. Create OAuth 2.0 credentials
    echo 4. Download as 'credentials.json' and place in this folder
    echo 5. See USER_GUIDE.md for detailed instructions
    echo.
) else (
    echo ✅ credentials.json found!
)

REM Create example config if it doesn't exist
if not exist "delete_config.json" (
    echo ⚙️  Creating example configuration...
    echo {> delete_config.json
    echo   "older_than_days": 180,>> delete_config.json
    echo   "exclude_with_attachments": true,>> delete_config.json
    echo   "exclude_important": true,>> delete_config.json
    echo   "exclude_starred": true,>> delete_config.json
    echo   "dry_run": true>> delete_config.json
    echo }>> delete_config.json
    echo ✅ Created delete_config.json with safe defaults
)

echo.
echo 🎉 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Get Gmail API credentials (see USER_GUIDE.md)
echo 2. Test with: venv\Scripts\activate.bat ^&^& python gmail_bulk_delete.py
echo 3. Configure rules in delete_config.json
echo 4. Run actual cleanup when ready
echo.
echo 📖 Read USER_GUIDE.md for complete instructions
echo 🛡️  Remember: Tool starts in safe dry-run mode
pause