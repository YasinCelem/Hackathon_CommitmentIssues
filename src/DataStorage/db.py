import os
from pymongo import MongoClient
from typing import Optional

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://testdb:test12345@commitment-issues-clust.2uplkb6.mongodb.net/?retryWrites=true&w=majority")
DEFAULT_DB_NAME = os.getenv("MONGO_DB", "Zane_Dima")

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    return _client

def username_to_db_name(username: str) -> str:
    """
    Convert username to database name format.
    Example: "ZaneDima" -> "Zane_Dima"
    """
    if not username:
        return DEFAULT_DB_NAME
    
    result = []
    for i, char in enumerate(username):
        if char.isupper() and i > 0 and username[i-1].islower():
            result.append('_')
        result.append(char)
    
    db_name = ''.join(result)
    return db_name

def get_db(db_name: Optional[str] = None):
    """
    Get database instance.
    If db_name is provided, use that database.
    Otherwise, use the default database.
    """
    if db_name:
        return get_client()[db_name]
    return get_client()[DEFAULT_DB_NAME]

def get_user_db(username: str):
    """
    Get user-specific database based on username.
    Example: username "ZaneDima" -> database "Zane_Dima"
    """
    db_name = username_to_db_name(username)
    return get_client()[db_name]

