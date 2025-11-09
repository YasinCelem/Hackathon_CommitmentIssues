# llm_main.py
import os
import re
import json
import time
import requests

import llm_functions  # your module

# ---------- Config ----------
BASE_URL = os.getenv("DOCS_API_BASE_URL", "http://localhost:5001")
POST_URL = f"{BASE_URL}/api/docs/"
GET_URL = f"{BASE_URL}/api/docs/?limit=1"  # lightweight reachability check
TIMEOUT = int(os.getenv("DOCS_API_TIMEOUT", "300"))  # seconds
REQUIRED = {"category", "name", "deadlines"}


# ---------- Helpers ----------
def clean_text(s: str) -> str:
    """Remove BOM / non-breaking spaces that can break json.loads."""
    if not isinstance(s, str):
        return s
    return s.replace("\ufeff", "").replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")


def extract_json_from_text(s: str) -> dict:
    """
    Accepts:
      - plain JSON string
      - fenced blocks like:
          ```json
          { ... }
          ```
      - or a blob containing a {...} JSON object
    Returns a Python dict or raises.
    """
    s = clean_text(s).strip()

    # 1) Try direct JSON
    try:
        return json.loads(s)
    except Exception:
        pass

    # 2) Strip ```json ... ``` fences
    fence = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)
    m = fence.search(s)
    if m:
        inner = m.group(1).strip()
        return json.loads(inner)

    # 3) Fallback: first {...} block
    obj = re.search(r"\{[\s\S]*\}", s)
    if obj:
        return json.loads(obj.group(0))

    raise ValueError("Could not find valid JSON in LLM output.")


def normalize_deadlines(deadlines):
    """
    Accept [date, desc] or [date, desc, recurrence];
    normalize to [date|None, desc, recurrence|None].
    """
    if not isinstance(deadlines, list):
        raise ValueError("deadlines must be an array")
    out = []
    for i, row in enumerate(deadlines):
        if not isinstance(row, list) or not (2 <= len(row) <= 3):
            raise ValueError(f"deadlines[{i}] must have 2 or 3 items")
        date = row[0] if row[0] not in (None, "", "null") else None
        desc = row[1]
        if not isinstance(desc, str) or not desc.strip():
            raise ValueError(f"deadlines[{i}].description must be a non-empty string")
        rec = None
        if len(row) == 3 and row[2] not in (None, "", "null"):
            if not isinstance(row[2], str):
                raise ValueError(f"deadlines[{i}].recurrence must be string or null")
            rec = row[2]
        out.append([date, desc.strip(), rec])
    return out


def wait_for_server(url: str, total_wait: int = 30) -> bool:
    """Poll the API briefly so we fail early on connection issues (WinError 10061)."""
    deadline = time.time() + total_wait
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:  # 2xx/4xx is fine for reachability
                return True
        except requests.exceptions.RequestException as e:
            last_err = e
        time.sleep(1)
    print(f"⚠️ API not reachable at {url} after {total_wait}s. Last error: {last_err}")
    return False


# ---------- Main ----------
def main():
    # 1) Generate LLM output (blocks until finished)
    print("⏳ Generating document with LLM…")
    raw = llm_functions.document_analyzer("../test_files/rental_contract_text.txt")
    print("✅ LLM generation done.")

    # 2) Extract JSON from the string
    try:
        payload = extract_json_from_text(raw)
    except Exception as e:
        print("❌ Failed to parse LLM JSON:", e)
        print("---- RAW LLM OUTPUT (first 600 chars) ----")
        print(clean_text(raw)[:600])
        return

    # 3) Minimal validation + normalization
    missing = REQUIRED - set(payload.keys())
    if missing:
        print(f"❌ Missing required fields: {', '.join(sorted(missing))}")
        return

    dr = payload.get("date_received")
    payload["date_received"] = None if dr in ("", "null") else dr
    payload["deadlines"] = normalize_deadlines(payload["deadlines"])

    # 4) Ensure API is up before posting (nice UX)
    if not wait_for_server(GET_URL, total_wait=30):
        print("❌ Could not connect to the API. Is it running on the correct port?")
        return

    # 5) POST with long timeout
    try:
        print("🚀 Sending document to API…")
        res = requests.post(POST_URL, json=payload, timeout=TIMEOUT)
        print("Status:", res.status_code)
        try:
            print("Response:", res.json())
        except Exception:
            print("Response (raw):", res.text)
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Connection timed out after {TIMEOUT} seconds.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Is the API listening on the right port?")
    except Exception as e:
        print("Unexpected error:", e)


if __name__ == "__main__":
    main()
