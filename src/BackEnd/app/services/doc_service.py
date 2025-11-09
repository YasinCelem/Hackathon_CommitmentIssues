from ..db import get_db
from flask import jsonify, request
from datetime import datetime
from bson import ObjectId
from datetime import datetime, date

def _now_iso():
    return datetime.utcnow().isoformat()

def _today_str():
    return date.today().strftime("%Y-%m-%d")

def _mk_item(date_val, desc, recurrence):
    return {
        "_state_id": str(ObjectId()),
        "date": date_val,            # may be None
        "description": desc,
        "recurrence": recurrence,    # may be None
    }

def _col():
    return get_db()["documents"]

def _json_error(msg, code=400):
    return jsonify(success=False, message=msg), code

def _json_ok(payload=None, code=200, **kw):
    base = {"success": True}
    if payload is not None:
        base |= payload
    if kw:
        base |= kw
    return jsonify(base), code

def _load_json(required=()):
    data = request.get_json(silent=True)
    if not data:
        return None, "Invalid or missing JSON body"
    missing = [k for k in required if k not in data]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"
    return data, None

def _validate_date_yyyy_mm_dd(value, field_name="date"):
    if value in (None, "", "null"):
        return None, None  # normalize emptyish to None
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value, None
    except ValueError:
        return None, f"Invalid {field_name} format, expected YYYY-MM-DD"

def _validate_and_normalize_deadlines(deadlines):
    """
    Accepts:
      - list of arrays: [date, description] or [date, description, recurrence]
    Normalizes:
      -> each entry becomes [date_or_None, description, recurrence_or_None]
    """
    if not isinstance(deadlines, list):
        return None, "deadlines must be an array"

    normalized = []
    for idx, item in enumerate(deadlines):
        if not isinstance(item, (list, tuple)):
            return None, f"deadlines[{idx}] must be an array"

        if not (2 <= len(item) <= 3):
            return None, "Each deadline must be [date, description] or [date, description, recurrence]"

        date_val, desc = item[0], item[1]
        recurrence = item[2] if len(item) == 3 else None

        # date format
        date_val, err = _validate_date_yyyy_mm_dd(date_val, f"deadlines[{idx}].date")
        if err:
            return None, err

        # description must be a non-empty string
        if not isinstance(desc, str) or not desc.strip():
            return None, f"deadlines[{idx}].description must be a non-empty string"

        # recurrence: null/None or string
        if recurrence not in (None, "null") and not isinstance(recurrence, str):
            return None, f"deadlines[{idx}].recurrence must be null or string"
        recurrence = None if recurrence in (None, "null") else recurrence

        normalized.append([date_val, desc, recurrence])

    return normalized, None