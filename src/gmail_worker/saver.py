import base64, json, shutil, uuid
from pathlib import Path
from typing import Dict, Iterator, List
from .config import ATTACH_DIR
from .gmail_client import gmail_service

def _iter_parts(payload: Dict) -> Iterator[Dict]:
    if not payload:
        return
    parts = payload.get("parts")
    if parts:
        for p in parts:
            yield from _iter_parts(p)
    else:
        yield payload

def _headers(msg: Dict) -> Dict[str, str]:
    def get(name: str) -> str:
        for h in msg.get("payload", {}).get("headers", []):
            if h.get("name") == name:
                return h.get("value", "")
        return ""
    return {
        "from": get("From"),
        "to": get("To"),
        "subject": get("Subject"),
        "date": get("Date"),
        "message_id": get("Message-Id") or msg.get("id", ""),
        "thread_id": msg.get("threadId", ""),
    }

def save_attachments_with_metadata(message: Dict) -> List[Dict]:
    """
    For each attachment in the Gmail message:
      - save <docId>_<safe-filename> into ATTACH_DIR
      - write <same-name>.json with email + attachment metadata
    Returns: list of {"file", "meta"} for saved items.
    """
    svc = gmail_service()
    msg_id = message["id"]
    hdr = _headers(message)
    saved: List[Dict] = []

    for part in _iter_parts(message.get("payload")):
        filename = (part.get("filename") or "").strip()
        body = part.get("body", {}) or {}
        att_id = body.get("attachmentId")
        mime = part.get("mimeType", "")
        size_hint = body.get("size", 0)

        # Only real attachments (skip inline/no-filename parts)
        if not att_id or not filename:
            continue

        # Fetch bytes
        att = svc.users().messages().attachments().get(
            userId="me", messageId=msg_id, id=att_id
        ).execute()
        data_b64 = att.get("data", "")
        blob = base64.urlsafe_b64decode(data_b64.encode("utf-8"))

        # Create deterministic-safe filenames
        doc_id = uuid.uuid4().hex
        safe = filename.replace("/", "_").replace("\\", "_")
        out_pdf = ATTACH_DIR / f"{doc_id}_{safe}"
        tmp_pdf = out_pdf.with_suffix(out_pdf.suffix + ".tmp")

        # Write file atomically
        tmp_pdf.write_bytes(blob)
        tmp_pdf.replace(out_pdf)

        # Write sidecar metadata
        meta = {
            "doc_id": doc_id,
            "file": str(out_pdf),
            "attachment": {
                "original_filename": filename,
                "mime_type": mime,
                "size_bytes": len(blob) or size_hint,
            },
            "email": hdr,
        }
        out_json = out_pdf.with_suffix(out_pdf.suffix + ".json")
        tmp_json = out_json.with_suffix(out_json.suffix + ".tmp")
        tmp_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        tmp_json.replace(out_json)

        saved.append({"file": str(out_pdf), "meta": meta})

    return saved
