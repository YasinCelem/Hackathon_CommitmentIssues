import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://testdb:test12345@commitment-issues-clust.2uplkb6.mongodb.net/?retryWrites=true&w=majority")
DB_NAME   = os.getenv("MONGO_DB", "financial_commitments")

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    return _client

def get_db():
    return get_client()[DB_NAME]
