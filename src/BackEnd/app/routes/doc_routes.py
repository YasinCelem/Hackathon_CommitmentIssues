from datetime import datetime
from urllib import request
from flask import Blueprint
from ..services import doc_service
from bson import ObjectId

docs_bp = Blueprint("documents", __name__, url_prefix="/api/docs")

@docs_bp.get("/")
def list_docs():
    """
    List all documents
    ---
    tags:
      - Documents
    produces:
      - application/json
    responses:
      200:
        description: OK
        schema:
          type: object
          properties:
            documents:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: "6760f3d58d9b0b9a4c4a2f30"
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
                      Array of arrays. Each item is [date, description, recurrence].
                      Date is YYYY-MM-DD or null; recurrence is optional.
                    items:
                      type: array
                      items:
                        type: string
                    example:
                      - ["2025-12-01", "File tax return", "yearly"]
                      - ["2025-12-15", "Submit payment"]
    """
    docs = []
    for doc in doc_service._col().find():
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return doc_service._json_ok({"documents": docs})

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
    data, err = doc_service._load_json(required=("category", "name", "deadlines"))
    if err:
        return doc_service._json_error(err)

    # date_received normalization
    date_received, err = doc_service._validate_date_yyyy_mm_dd(data.get("date_received"), "date_received")
    if err:
        return doc_service._json_error(err)
    data["date_received"] = date_received

    # deadlines: variable length inner arrays (2..3); normalize to 3-tuple shape
    deadlines_norm, d_err = doc_service._validate_and_normalize_deadlines(data.get("deadlines"))
    if d_err:
        return doc_service._json_error(d_err)
    data["deadlines"] = [doc_service._mk_item(d[0], d[1], d[2]) for d in deadlines_norm]
    data["pending"] = []
    data["complete"] = []
    data["overdue"] = []

    now_iso = datetime.utcnow().isoformat()
    data["created_at"] = now_iso
    data["updated_at"] = now_iso

    res = doc_service._col().insert_one(data)
    return doc_service._json_ok({"id": str(res.inserted_id), "message": "Document added successfully"}, code=201)

# def _ensure_lists(doc):
#     # Make sure arrays exist (avoids KeyErrors on legacy docs)
#     for k in ("deadlines", "pending", "complete", "overdue"):
#         if k not in doc or not isinstance(doc[k], list):
#             doc[k] = []
#     return doc

@docs_bp.patch("/<doc_id>/pending")
def pending_deadline(doc_id):
    """
    Move one item from deadlines -> pending
    ---
    tags: [Documents]
    parameters:
      - in: path
        name: doc_id
        required: true
        schema: { type: string }
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            state_id: { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
          required: [state_id]
    responses:
      200: { description: Moved }
      404: { description: Not found }
    """
    data, err = doc_service._load_json(required=("state_id",))
    if err:
        return doc_service._json_error(err)

    # 1) Load doc
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return doc_service._json_error("Invalid doc_id", 404)

    doc = doc_service._col().find_one({"_id": oid})
    if not doc:
        return doc_service._json_error("Document not found", 404)

    # 2) Ensure arrays exist
    deadlines = doc.get("deadlines") or []
    if not isinstance(deadlines, list):
        deadlines = []
    pending = doc.get("pending") or []
    if not isinstance(pending, list):
        pending = []

    # 3) Locate by _state_id (NOT _id)
    state_id = str(data["state_id"])
    idx = next(
        (i for i, it in enumerate(deadlines) if str(it.get("_state_id")) == state_id),
        None
    )
    if idx is None:
        return doc_service._json_error("Item not found in deadlines", 404)

    # 4) Move item -> pending
    item = deadlines.pop(idx)
    item["pending_at"] = doc_service._now_iso()

    # avoid duplicates in pending (by _state_id)
    pending = [it for it in pending if str(it.get("_state_id")) != state_id]
    pending.append(item)

    # 5) Recompute state based on the new snapshot
    updated_snapshot = {**doc, "deadlines": deadlines, "pending": pending}
    new_state = doc_service._recompute_state(updated_snapshot)

    new_doc = {
        "deadlines": deadlines,
        "pending": pending,
        "updated_at": doc_service._now_iso(),
    }
    doc_service._col().update_one({"_id": doc["_id"]}, {"$set": new_doc})

    return doc_service._json_ok({
        "moved": state_id,
        "pending_count": len(pending),
        "deadlines_count": len(deadlines),
    })

@docs_bp.patch("/<doc_id>/complete")
def complete_pending(doc_id):
    """
    Move one item from pending -> complete
    ---
    tags: [Documents]
    parameters:
      - in: path
        name: doc_id
        required: true
        schema: { type: string }
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            state_id: { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
          required: [state_id]
    responses:
      200: { description: Moved }
      404: { description: Not found }
    """
    data, err = doc_service._load_json(required=("state_id",))
    if err:
        return doc_service._json_error(err)

    # 1) Load doc
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return doc_service._json_error("Invalid doc_id", 404)

    doc = doc_service._col().find_one({"_id": oid})
    if not doc:
        return doc_service._json_error("Document not found", 404)

    # 2) Ensure arrays exist
    pending = doc.get("pending") or []
    if not isinstance(pending, list):
        pending = []
    complete = doc.get("complete") or []
    if not isinstance(complete, list):
        complete = []

    # 3) Locate by _state_id (NOT _id)
    state_id = str(data["state_id"])
    idx = next(
        (i for i, it in enumerate(pending) if str(it.get("_state_id")) == state_id),
        None
    )
    if idx is None:
        return doc_service._json_error("Item not found in pending", 404)

    # 4) Move item -> complete
    item = pending.pop(idx)
    item["completed_at"] = doc_service._now_iso()

    # avoid duplicates in complete (by _state_id)
    complete = [it for it in complete if str(it.get("_state_id")) != state_id]
    complete.append(item)

    # 5) Recompute state based on the new snapshot
    updated_snapshot = {**doc, "pending": pending, "complete": complete}
    new_state = doc_service._recompute_state(updated_snapshot)

    new_doc = {
        "pending": pending,
        "complete": complete,
        "updated_at": doc_service._now_iso(),
    }
    doc_service._col().update_one({"_id": doc["_id"]}, {"$set": new_doc})

    return doc_service._json_ok({
        "moved": state_id,
        "pending_count": len(pending),
        "complete_count": len(complete),
    })

@docs_bp.patch("/<doc_id>/overdue")
def mark_overdue(doc_id):
    """
    Move one item from deadlines -> overdue
    ---
    tags: [Documents]
    parameters:
      - in: path
        name: doc_id
        required: true
        schema: { type: string }
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            state_id: { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
          required: [state_id]
    responses:
      200: { description: Moved }
      404: { description: Not found }
    """
    data, err = doc_service._load_json(required=("state_id",))
    if err:
        return doc_service._json_error(err)

    # 1) Load doc
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return doc_service._json_error("Invalid doc_id", 404)

    doc = doc_service._col().find_one({"_id": oid})
    if not doc:
        return doc_service._json_error("Document not found", 404)

    # 2) Ensure arrays exist
    deadlines = doc.get("deadlines") or []
    if not isinstance(deadlines, list):
        deadlines = []
    overdue = doc.get("overdue") or []
    if not isinstance(overdue, list):
        overdue = []

    # 3) Locate by _state_id (NOT _id)
    state_id = str(data["state_id"])
    idx = next(
        (i for i, it in enumerate(deadlines) if str(it.get("_state_id")) == state_id),
        None
    )
    if idx is None:
        return doc_service._json_error("Item not found in deadlines", 404)

    # 4) Move item -> overdue
    item = deadlines.pop(idx)
    item["marked_overdue_at"] = doc_service._now_iso()

    # avoid duplicates in overdue (by _state_id)
    overdue = [it for it in overdue if str(it.get("_state_id")) != state_id]
    overdue.append(item)

    # 5) Recompute state based on the new snapshot
    updated_snapshot = {**doc, "deadlines": deadlines, "overdue": overdue}
    new_state = doc_service._recompute_state(updated_snapshot)

    new_doc = {
        "deadlines": deadlines,
        "overdue": overdue,
        "updated_at": doc_service._now_iso(),
    }
    doc_service._col().update_one({"_id": doc["_id"]}, {"$set": new_doc})

    return doc_service._json_ok({
        "moved": state_id,
        "overdue_count": len(overdue),
        "deadlines_count": len(deadlines),
    })