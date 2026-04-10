# Gmail Bulk Delete

Ultra-fast Gmail cleanup tool. Async processing, smart filtering, 83+ emails/second. Protects your important messages and attachments.

## What It Does

- Deletes thousands of old emails in minutes (83+ emails/sec)
- Preserves emails with attachments, starred, and important
- Moves to trash (recoverable for 30 days, not permanent)
- Dry-run mode to preview before deleting
- Filter presets for common cleanup tasks

## Quick Start

### 1. Setup

```bash
git clone https://github.com/adrozdenko/gmail_bulk_delete.git
cd gmail_bulk_delete
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable the **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop app type)
5. Download as `credentials.json` into the project directory
6. Add your email as a test user in the OAuth consent screen

Then generate your token:

```bash
python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    ['https://www.googleapis.com/auth/gmail.modify']
)
creds = flow.run_local_server(port=0)
with open('token.pickle', 'wb') as f:
    pickle.dump(creds, f)
print('Done!')
"
```

### 3. Run

```bash
python3 main.py
```

You'll see a preset menu:

```
FILTER PRESETS:
==================================================
   1. Default - 6 months old, preserve attachments
   2. Newsletter cleanup - 30 days, newsletter keywords
   3. GitHub notifications - 7 days old
   4. Large emails - 90 days, 10MB+ size
   5. Social media - 14 days, FB/Twitter/LinkedIn
   6. Promotional emails - 60 days, sale keywords
   7. Custom filters (advanced)

Choose preset (1-7) [1]:

Dry run? (y/N):
```

## Filter Presets

| Preset | What It Cleans | Age | Details |
|--------|---------------|-----|---------|
| Default | Everything except attachments | 6 months | Preserves important + starred |
| Newsletters | Marketing emails | 30 days | Newsletter keywords + domains |
| GitHub | Dev notifications | 7 days | GitHub-specific senders |
| Large Emails | 10MB+ emails | 90 days | Size-based cleanup |
| Social Media | FB/Twitter/LinkedIn | 14 days | Social platform domains |
| Promotional | Sales/discount emails | 60 days | Promo keywords |
| Custom | Your rules | You choose | Full control |

## Safety

**Always protected (never deleted):**
- Emails with attachments
- Important emails
- Starred emails
- Emails newer than your age filter

**Safety features:**
- Dry-run mode (preview what will be deleted)
- Moves to trash (not permanent -- recoverable for 30 days)
- Rate limit handling with automatic backoff
- Batch processing with error recovery

## Architecture

```
main.py                          # Single entry point
models/
  filter_config.py               # FilterConfig dataclass
  deletion_result.py             # Result models
services/
  gmail_client.py                # Gmail API connection + pooling
  query_builder.py               # Gmail search query builder
  email_deleter.py               # Batch + individual deletion
  deletion_orchestrator.py       # Main orchestration loop
  performance_tracker.py         # Rate + memory monitoring
utils/
  ui.py                          # Display helpers + preset menu
constants.py                     # Configuration constants
tests/                           # 119 tests, 96% coverage
```

## Performance

- 83+ emails/second with async batch API
- 5 concurrent async tasks
- 300 emails per chunk, 60 per task
- Connection pooling (single service reuse)
- Automatic garbage collection
- Smart rate limiting with exponential backoff

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
pytest tests/ --cov --cov-report=term-missing
```

119 tests, 96% coverage, 0.80 seconds, zero real API calls.

## Requirements

- Python 3.9+
- Gmail account
- Google Cloud project with Gmail API enabled

## License

MIT
