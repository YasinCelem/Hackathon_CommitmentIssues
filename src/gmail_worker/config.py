import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Where to put downloaded files + metadata
ATTACH_DIR = Path(os.environ.get("GMAIL_ATTACH_DIR", BASE_DIR / "downloads"))
ATTACH_DIR.mkdir(parents=True, exist_ok=True)

# OAuth files (put credentials.json here or point with env)
CREDENTIALS_PATH = Path(os.environ.get("GOOGLE_CREDENTIALS_JSON", BASE_DIR / "credentials.json"))
TOKEN_PATH       = Path(os.environ.get("GOOGLE_TOKEN_JSON",       BASE_DIR / "token.json"))

# Gmail scopes (read/modify to optionally mark as read if you want later)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Poll settings (keep broad; we de-dupe by message id)
QUERY = os.environ.get("GMAIL_POLL_QUERY", "in:inbox is:unread newer_than:7d")
POLL_SECONDS = int(os.environ.get("GMAIL_POLL_SECONDS", "5"))

# Simple de-dupe state
STATE_PATH = BASE_DIR / "processed_ids.json"
