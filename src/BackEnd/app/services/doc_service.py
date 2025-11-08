# from ..db import get_db
# from bson import ObjectId
# from werkzeug.security import generate_password_hash, check_password_hash
# from typing import Optional

# def _collection():
#     return get_db()["documents"]

# def list_documents(category: str | None = None) -> list[dict]:
#     query = {"category": category} if category else {}
#     docs = list(_collection().find(query))
#     for d in docs:
#         d["_id"] = str(d["_id"])
#     return docs

# def _validate_and_normalize(payload: dict) -> tuple[bool, str | None, dict | None]:
#     if not payload:
#         return False, "Invalid or missing JSON body", None

#     required = ["category", "name", "deadlines"]
#     missing = [f for f in required if f not in payload]
#     if missing:
#         return False, f"Missing fields: {', '.join(missing)}", None

#     # date_received normalization
#     dr = payload.get("date_received")
#     if dr and dr != "null":
#         try:
#             datetime.strptime(dr, "%Y-%m-%d")
#         except ValueError:
#             return False, "Invalid date_received format, expected YYYY-MM-DD", None
#     else:
#         payload["date_received"] = None

#     # deadlines: list of [date, description, recurrence/null]
#     for item in payload.get("deadlines", []):
#         if not isinstance(item, list) or len(item) != 3:
#             return False, "Each deadline must be [date, description, recurrence/null]", None

#     payload["created_at"] = datetime.utcnow().isoformat()
#     return True, None, payload

# def create_document(payload: dict) -> tuple[bool, str, str | None]:
#     ok, err, normalized = _validate_and_normalize(payload)
#     if not ok:
#         return False, err, None
#     res = _collection().insert_one(normalized)
#     return True, "Document added successfully", str(res.inserted_id)

# def update_document(doc_id: str, updates: dict) -> tuple[bool, str]:
#     if not updates:
#         return False, "Missing update data"
#     try:
#         oid = ObjectId(doc_id)
#     except Exception:
#         return False, "Invalid document id"

#     result = _collection().update_one({"_id": oid}, {"$set": updates})
#     if result.matched_count == 0:
#         return False, "Document not found"
#     return True, "Document updated successfully"

# def delete_document(doc_id: str) -> tuple[bool, str]:
#     try:
#         oid = ObjectId(doc_id)
#     except Exception:
#         return False, "Invalid document id"
#     result = _collection().delete_one({"_id": oid})
#     if result.deleted_count == 0:
#         return False, "Document not found"
#     return True, "Document deleted successfully"
