from ..db import get_db

def list_all():
    return get_db()["users"].find().sort("_id", -1)

def create(document: dict) -> str:
    res = get_db()["users"].insert_one(document)
    return str(res.inserted_id)
