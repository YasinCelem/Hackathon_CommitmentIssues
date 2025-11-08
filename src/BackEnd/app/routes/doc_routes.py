from datetime import datetime
from flask import Blueprint, jsonify, request
from ..db import get_db

docs_bp = Blueprint("documents", __name__, url_prefix="/api/docs")

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

@docs_bp.post("/")
def add_doc():
    """
    Add a new document
    ---
    tags:
      - Documents
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            category:
              type: string
              example: "financial"
            name:
              type: string
              example: "2025-11-08 - TaxReturn - IRS - 1040Submission"
            date_received:
              type: string
              format: date
              x-nullable: true
              example: "2025-11-01"
            deadlines:
              type: array
              description: >
                Array of arrays. Each item is [date, description] or
                [date, description, recurrence]. Date is YYYY-MM-DD or null.
              items:
                type: array
                items:
                  type: string
              example:
                - ["2025-12-01", "File tax return", "yearly"]
                - ["2025-12-15", "Submit payment"]
          required:
            - category
            - name
            - deadlines
    responses:
      201:
        description: Created
        schema:
          type: object
          properties:
            id:
              type: string
              example: "6760f3d58d9b0b9a4c4a2f30"
            message:
              type: string
              example: "Document added successfully"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing fields: category, name"
    """
    data, err = _load_json(required=("category", "name", "deadlines"))
    if err:
        return _json_error(err)

    # date_received normalization
    date_received, err = _validate_date_yyyy_mm_dd(data.get("date_received"), "date_received")
    if err:
        return _json_error(err)
    data["date_received"] = date_received

    # deadlines: variable length inner arrays (2..3); normalize to 3-tuple shape
    deadlines_norm, d_err = _validate_and_normalize_deadlines(data.get("deadlines"))
    if d_err:
        return _json_error(d_err)
    data["deadlines"] = deadlines_norm

    now_iso = datetime.utcnow().isoformat()
    data["created_at"] = now_iso
    data["updated_at"] = now_iso

    res = _col().insert_one(data)
    return _json_ok({"id": str(res.inserted_id), "message": "Document added successfully"}, code=201)
