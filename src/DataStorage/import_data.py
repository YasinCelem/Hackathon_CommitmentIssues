import json
import os
from pathlib import Path
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        data = json_util.loads(content)
        return data if isinstance(data, list) else [data]


def import_collection(client, db_name, collection_name, file_path):
    db = client[db_name]
    collection = db[collection_name]
    
    if not os.path.exists(file_path):
        print(f"  [FAIL] File not found: {file_path}")
        return False
    
    try:
        data = load_json_file(file_path)
        
        if data:
            result = collection.insert_many(data)
            print(f"  [PASS] {collection_name}: Inserted {len(result.inserted_ids)} documents")
            return True
        else:
            print(f"  [FAIL] {collection_name}: No data to import")
            return False
    except Exception as e:
        print(f"  [FAIL] {collection_name}: Error - {e}")
        return False


def main():
    connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGODB_DB', 'hackathon')
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    
    print(f"MongoDB URI: {connection_string}")
    print(f"Database: {database_name}")
    print(f"Profile Data Path: {profile_path}")
    print()
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("[PASS] Connected to MongoDB")
    except Exception as e:
        print(f"[FAIL] Failed to connect to MongoDB: {e}")
        return
    
    collections = {
        'users': 'users.json',
        'companies': 'companies.json',
        'bank_accounts': 'bank_accounts.json',
        'documents': 'documents.json',
        'settings': 'settings.json',
        'sessions': 'sessions.json'
    }
    
    base_path = Path(__file__).parent.parent.parent
    profile_full_path = base_path / profile_path
    
    print(f"Importing data from: {profile_full_path}")
    print()
    
    imported = 0
    for collection_name, filename in collections.items():
        file_path = profile_full_path / filename
        print(f"Importing {collection_name}...")
        if import_collection(client, database_name, collection_name, file_path):
            imported += 1
        print()
    
    print("Creating indexes...")
    db = client[database_name]
    
    try:
        db.users.create_index("email", unique=True)
        print("  [PASS] users.email (unique)")
    except Exception as e:
        print(f"  [FAIL] users.email: {e}")
    
    try:
        db.companies.create_index("kvk_number", unique=True)
        print("  [PASS] companies.kvk_number (unique)")
    except Exception as e:
        print(f"  [FAIL] companies.kvk_number: {e}")
    
    try:
        db.bank_accounts.create_index("company_id")
        print("  [PASS] bank_accounts.company_id")
    except Exception as e:
        print(f"  [FAIL] bank_accounts.company_id: {e}")
    
    try:
        db.documents.create_index([
            ("company_id", 1),
            ("type", 1),
            ("period", 1),
            ("date", -1)
        ])
        print("  [PASS] documents (company_id, type, period, date)")
    except Exception as e:
        print(f"  [FAIL] documents: {e}")
    
    print()
    print(f"[PASS] Import complete! {imported}/{len(collections)} collections imported")
    
    client.close()


if __name__ == "__main__":
    main()
