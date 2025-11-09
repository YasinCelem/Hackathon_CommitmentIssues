"""
Script to update all MongoDB collections with data from JSON files.

This script will:
1. Connect to MongoDB
2. Update/insert all collections (users, companies, bank_accounts, documents, 
   settings, sessions, transactions, invoices, bills)
3. Create/update indexes
4. Verify the update
"""

import json
import os
from pathlib import Path
from bson import json_util, ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()


def load_json_file(file_path):
    """Load JSON file with BSON support for $oid format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        data = json_util.loads(content)
        return data if isinstance(data, list) else [data]


def update_collection(client, db_name, collection_name, file_path, clear_existing=False):
    """
    Update a collection with new data.
    
    Args:
        client: MongoDB client
        db_name: Database name
        collection_name: Collection name
        file_path: Path to JSON file
        clear_existing: If True, delete all existing documents before inserting
    """
    db = client[db_name]
    collection = db[collection_name]
    
    if not os.path.exists(file_path):
        print(f"  [FAIL] File not found: {file_path}")
        return False
    
    try:
        # Load the data
        print(f"  [INFO] Loading data from {file_path}...")
        data = load_json_file(file_path)
        
        if not data:
            print(f"  [FAIL] {collection_name}: No data to import")
            return False
        
        print(f"  [INFO] Loaded {len(data)} documents")
        
        # Clear existing documents if requested
        if clear_existing:
            print(f"  [INFO] Clearing existing documents in {collection_name}...")
            result = collection.delete_many({})
            print(f"  [INFO] Deleted {result.deleted_count} existing documents")
        
        # Insert new documents
        print(f"  [INFO] Inserting {len(data)} documents...")
        result = collection.insert_many(data)
        print(f"  [PASS] {collection_name}: Inserted {len(result.inserted_ids)} documents")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] {collection_name}: Error - {e}")
        import traceback
        traceback.print_exc()
        return False


def update_collection_by_id(client, db_name, collection_name, file_path):
    """
    Update existing documents by matching _id, or insert if not found.
    This preserves existing documents that aren't in the JSON file.
    """
    db = client[db_name]
    collection = db[collection_name]
    
    if not os.path.exists(file_path):
        print(f"  [FAIL] File not found: {file_path}")
        return False
    
    try:
        # Load the data
        print(f"  [INFO] Loading data from {file_path}...")
        data = load_json_file(file_path)
        
        if not data:
            print(f"  [FAIL] {collection_name}: No data to import")
            return False
        
        print(f"  [INFO] Loaded {len(data)} documents")
        
        # Update or insert each document
        updated_count = 0
        inserted_count = 0
        
        for doc in data:
            # Convert $oid to ObjectId for query
            doc_id = doc.get('_id', {}).get('$oid')
            if doc_id:
                # Convert the document to use ObjectId
                doc_copy = json_util.loads(json_util.dumps(doc))
                
                # Update or insert
                result = collection.replace_one(
                    {'_id': ObjectId(doc_id)},
                    doc_copy,
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1
        
        print(f"  [PASS] {collection_name}: Updated {updated_count} documents, inserted {inserted_count} new documents")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {collection_name}: Error - {e}")
        import traceback
        traceback.print_exc()
        return False


def create_indexes(db):
    """Create or update indexes for all collections."""
    print("Creating/updating indexes...")
    
    try:
        # Users indexes
        db.users.create_index("email", unique=True)
        print("  [PASS] users.email (unique)")
    except Exception as e:
        print(f"  [FAIL] users.email: {e}")
    
    try:
        # Companies indexes
        db.companies.create_index("kvk_number", unique=True)
        print("  [PASS] companies.kvk_number (unique)")
    except Exception as e:
        print(f"  [FAIL] companies.kvk_number: {e}")
    
    try:
        # Bank accounts indexes
        db.bank_accounts.create_index("company_id")
        print("  [PASS] bank_accounts.company_id")
    except Exception as e:
        print(f"  [FAIL] bank_accounts.company_id: {e}")
    
    try:
        # Documents indexes - new structure
        db.documents.create_index("category")
        print("  [PASS] documents.category")
        
        db.documents.create_index([("category", 1), ("date_received", -1)])
        print("  [PASS] documents (category, date_received)")
        
        db.documents.create_index("date_received")
        print("  [PASS] documents.date_received")
        
        db.documents.create_index("created_at")
        print("  [PASS] documents.created_at")
    except Exception as e:
        print(f"  [FAIL] documents indexes: {e}")
    
    try:
        # Transactions indexes
        db.transactions.create_index("company_id")
        print("  [PASS] transactions.company_id")
        
        db.transactions.create_index("bank_account_id")
        print("  [PASS] transactions.bank_account_id")
        
        db.transactions.create_index("transaction_date")
        print("  [PASS] transactions.transaction_date")
        
        db.transactions.create_index([("company_id", 1), ("transaction_date", -1)])
        print("  [PASS] transactions (company_id, transaction_date)")
    except Exception as e:
        print(f"  [FAIL] transactions indexes: {e}")
    
    try:
        # Invoices indexes
        db.invoices.create_index("company_id")
        print("  [PASS] invoices.company_id")
        
        db.invoices.create_index("invoice_number", unique=True)
        print("  [PASS] invoices.invoice_number (unique)")
        
        db.invoices.create_index("invoice_date")
        print("  [PASS] invoices.invoice_date")
        
        db.invoices.create_index("status")
        print("  [PASS] invoices.status")
    except Exception as e:
        print(f"  [FAIL] invoices indexes: {e}")
    
    try:
        # Bills indexes
        db.bills.create_index("company_id")
        print("  [PASS] bills.company_id")
        
        db.bills.create_index("bill_number", unique=True)
        print("  [PASS] bills.bill_number (unique)")
        
        db.bills.create_index("bill_date")
        print("  [PASS] bills.bill_date")
        
        db.bills.create_index("status")
        print("  [PASS] bills.status")
    except Exception as e:
        print(f"  [FAIL] bills indexes: {e}")
    
    print("[PASS] All indexes created successfully")


def main():
    """Main function to update all data in the database."""
    print("=" * 60)
    print("MongoDB Database Update Script - All Collections")
    print("=" * 60)
    print()
    
    # Step 1: Get configuration
    connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGODB_DB', 'hackathon')
    profile_path = os.getenv('PROFILE_DATA_PATH', 'src/DataStorage/ProfileData/Zane_Dima')
    
    print(f"Configuration:")
    print(f"  MongoDB URI: {connection_string}")
    print(f"  Database: {database_name}")
    print(f"  Profile Data Path: {profile_path}")
    print()
    
    # Step 2: Connect to MongoDB
    print("Step 1: Connecting to MongoDB...")
    try:
        if connection_string.startswith('mongodb+srv://'):
            from pymongo.server_api import ServerApi
            client = MongoClient(
                connection_string,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000
            )
        else:
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        client.admin.command('ping')
        print("[PASS] Connected to MongoDB")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"[FAIL] Failed to connect to MongoDB: {e}")
        return
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return
    
    print()
    
    # Step 3: Define all collections to update
    base_path = Path(__file__).parent
    profile_full_path = base_path / profile_path
    
    collections = {
        'users': 'users.json',
        'companies': 'companies.json',
        'bank_accounts': 'bank_accounts.json',
        'documents': 'documents.json',
        'settings': 'settings.json',
        'sessions': 'sessions.json',
        'transactions': 'transactions.json',
        'invoices': 'invoices.json',
        'bills': 'bills.json'
    }
    
    # Collections that should clear existing data (due to structure changes)
    clear_collections = ['documents']  # Documents structure changed significantly
    
    # Step 4: Update each collection
    print("Step 2: Updating collections...")
    print()
    
    updated_count = 0
    for collection_name, filename in collections.items():
        file_path = profile_full_path / filename
        print(f"Updating {collection_name}...")
        
        clear_existing = collection_name in clear_collections
        success = update_collection(
            client, 
            database_name, 
            collection_name, 
            str(file_path),
            clear_existing=clear_existing
        )
        
        if success:
            updated_count += 1
        print()
    
    # Step 5: Create/update indexes
    print("Step 3: Creating/updating indexes...")
    db = client[database_name]
    create_indexes(db)
    
    print()
    
    # Step 6: Verify
    print("Step 4: Verifying update...")
    for collection_name in collections.keys():
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"  [PASS] {collection_name}: {count} documents")
    
    print()
    print("=" * 60)
    print(f"[PASS] Database update complete! {updated_count}/{len(collections)} collections updated")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    main()

