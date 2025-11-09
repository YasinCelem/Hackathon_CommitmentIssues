import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.DataStorage.db import get_db
from bson import ObjectId
from datetime import datetime
from typing import Optional, List, Dict


def _documents_collection(db_name: Optional[str] = None):
    """Return Mongo collection for documents in specified database."""
    db = get_db(db_name) if db_name else get_db()
    return db["documents"]


def list_documents(category: Optional[str] = None, user_id: Optional[str] = None, db_name: Optional[str] = None) -> List[Dict]:
    """List documents, optionally filtered by category and/or user_id."""
    query = {}
    if category:
        query["category"] = category
    if user_id:
        query["user_id"] = user_id
    
    docs = list(_documents_collection(db_name).find(query))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs


def find_document_by_id(doc_id: str, db_name: Optional[str] = None) -> Optional[Dict]:
    """Find a document by ObjectId string."""
    try:
        doc = _documents_collection(db_name).find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception:
        return None


def create_document(data: dict, db_name: Optional[str] = None) -> str:
    """Create a new document."""
    if "created_at" not in data:
        data["created_at"] = datetime.utcnow().isoformat()
    
    res = _documents_collection(db_name).insert_one(data)
    return str(res.inserted_id)


def update_document(doc_id: str, updates: dict, db_name: Optional[str] = None) -> bool:
    """Update a document by ID."""
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return False
    
    result = _documents_collection(db_name).update_one(
        {"_id": oid},
        {"$set": updates}
    )
    return result.modified_count > 0


def delete_document(doc_id: str, db_name: Optional[str] = None) -> bool:
    """Delete a document by ID."""
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return False
    
    result = _documents_collection(db_name).delete_one({"_id": oid})
    return result.deleted_count > 0

