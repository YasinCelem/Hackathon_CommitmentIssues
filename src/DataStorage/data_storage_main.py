import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()


class MongoDBConnection:
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connection_string = os.getenv(
            'MONGODB_URI', 
            'mongodb://localhost:27017/'
        )
        self.database_name = os.getenv('MONGODB_DB', 'hackathon')
    
    def connect(self):
        try:
            if self.connection_string.startswith('mongodb+srv://'):
                self.client = MongoClient(
                    self.connection_string,
                    server_api=ServerApi('1'),
                    serverSelectionTimeoutMS=5000
                )
            else:
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000
                )
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"[PASS] Connected to MongoDB: {self.database_name}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[FAIL] Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        if self.client:
            self.client.close()
            print("[PASS] Disconnected from MongoDB")
    
    def get_collection(self, collection_name):
        if not self.db:
            raise Exception("Not connected to MongoDB. Call connect() first.")
        return self.db[collection_name]
    
    def create_indexes(self):
        if not self.db:
            raise Exception("Not connected to MongoDB. Call connect() first.")
        
        print("Creating indexes...")
        
        self.db.users.create_index("email", unique=True)
        print("  [PASS] users.email (unique)")
        
        self.db.companies.create_index("kvk_number", unique=True)
        print("  [PASS] companies.kvk_number (unique)")
        
        self.db.bank_accounts.create_index("company_id")
        print("  [PASS] bank_accounts.company_id")
        
        self.db.documents.create_index([
            ("company_id", 1),
            ("type", 1),
            ("period", 1),
            ("date", -1)
        ])
        print("  [PASS] documents (company_id, type, period, date)")
        
        self.db.documents.create_index("category")
        print("  [PASS] documents.category")
        
        self.db.documents.create_index([
            ("category", 1),
            ("date_received", -1)
        ])
        print("  [PASS] documents (category, date_received)")
        
        print("[PASS] All indexes created successfully")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


_db_connection = None


def get_db_connection():
    global _db_connection
    if _db_connection is None:
        _db_connection = MongoDBConnection()
        _db_connection.connect()
    return _db_connection


def get_collection(collection_name):
    conn = get_db_connection()
    return conn.get_collection(collection_name)


if __name__ == "__main__":
    with MongoDBConnection() as db:
        if db.db:
            print(f"Database: {db.database_name}")
            print(f"Collections: {db.db.list_collection_names()}")
            db.create_indexes()
