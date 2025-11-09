import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.DataStorage.db import get_db
from typing import Optional


def _data_collection(db_name: Optional[str] = None):
    """Return Mongo collection for general data in specified database."""
    db = get_db(db_name) if db_name else get_db()
    return db["data"]


def list_all_data(db_name: Optional[str] = None):
    """List all data records (sorted newest first)."""
    return _data_collection(db_name).find().sort("_id", -1)


def create_data(document: dict, db_name: Optional[str] = None) -> str:
    """Create a new data record."""
    res = _data_collection(db_name).insert_one(document)
    return str(res.inserted_id)

