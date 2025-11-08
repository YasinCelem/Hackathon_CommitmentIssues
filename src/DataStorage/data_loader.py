import json
import os
import sys
from pathlib import Path
from bson import json_util
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.DataStorage.data_storage_main import get_db_connection, MongoDBConnection

load_dotenv()


def load_from_mongodb(collection_name):
    try:
        conn = get_db_connection()
        if conn and conn.db:
            collection = conn.get_collection(collection_name)
            data = list(collection.find({}))
            if data:
                return data
    except Exception as e:
        print(f"[FAIL] Could not load from MongoDB: {e}")
    return None


def load_from_local_file(file_path):
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json_util.loads(content)
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"[FAIL] Could not load from local file: {e}")
    return None


def get_data(collection_name, local_file_path=None):
    data = load_from_mongodb(collection_name)
    
    if data:
        print(f"[PASS] Loaded {len(data)} documents from MongoDB ({collection_name})")
        return data
    
    if local_file_path:
        data = load_from_local_file(local_file_path)
        if data:
            print(f"[PASS] Loaded {len(data)} documents from local file ({local_file_path})")
            return data
    
    print(f"[FAIL] No data found in MongoDB or local files for {collection_name}")
    return None


def get_users():
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    base_path = Path(__file__).parent.parent.parent
    local_file = base_path / profile_path / 'users.json'
    return get_data('users', str(local_file))


def get_companies():
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    base_path = Path(__file__).parent.parent.parent
    local_file = base_path / profile_path / 'companies.json'
    return get_data('companies', str(local_file))


def get_documents():
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    base_path = Path(__file__).parent.parent.parent
    local_file = base_path / profile_path / 'documents.json'
    return get_data('documents', str(local_file))


def get_bank_accounts():
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    base_path = Path(__file__).parent.parent.parent
    local_file = base_path / profile_path / 'bank_accounts.json'
    return get_data('bank_accounts', str(local_file))


if __name__ == "__main__":
    print("Testing interactive data loader...")
    print()
    
    users = get_users()
    if users:
        print(f"Found {len(users)} users")
    
    print()
    
    documents = get_documents()
    if documents:
        print(f"Found {len(documents)} documents")
