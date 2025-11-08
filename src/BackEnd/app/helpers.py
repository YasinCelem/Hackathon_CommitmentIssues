from bson import ObjectId

def to_json(doc: dict) -> dict:
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d

def to_oid(oid_str: str) -> ObjectId | None:
    try:
        return ObjectId(oid_str)
    except Exception:
        return None
