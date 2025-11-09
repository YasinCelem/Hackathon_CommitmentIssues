import json, time
from pathlib import Path
from .config import QUERY, STATE_PATH, POLL_SECONDS
from .gmail_client import gmail_service
from .saver import save_attachments_with_metadata
from ..main import decide_file_type 

def _load_state() -> set[str]:
    if STATE_PATH.exists():
        try:
            return set(json.loads(STATE_PATH.read_text() or "[]"))
        except Exception:
            return set()
    return set()

def _save_state(ids: set[str]):
    STATE_PATH.write_text(json.dumps(sorted(ids)))

import time
from .config import QUERY, POLL_SECONDS
from .gmail_client import gmail_service
from .saver import save_attachments_with_metadata

def run_poller():
    svc = gmail_service()
    print("[gmail] poller started (saving attachments + metadata)")

    while True:
        try:
            resp = svc.users().messages().list(userId="me", q=QUERY, maxResults=20).execute() or {}
            for m in resp.get("messages", []):
                mid = m["id"]
                full = svc.users().messages().get(userId="me", id=mid, format="full").execute()
                items = save_attachments_with_metadata(full)
                if items:
                    print(f"[gmail] saved {len(items)} attachment(s) from message {mid}")
                    decide_file_type()
        except Exception as e:
            print("[gmail] error:", e)

        time.sleep(POLL_SECONDS)

