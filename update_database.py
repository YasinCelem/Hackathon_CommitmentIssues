"""
Step-by-step script to update the MongoDB database with the new document structure.

This script will:
1. Connect to MongoDB
2. Clear existing documents (optional - can be configured)
3. Import the updated documents.json file
4. Update indexes
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


def update_documents_collection(client, db_name, collection_name, file_path, clear_existing=False):
    """
    Update the documents collection with new structure.
    
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
        # Step 1: Load the new data
        print(f"  [INFO] Loading data from {file_path}...")
        data = load_json_file(file_path)
        
        if not data:
            print(f"  [FAIL] {collection_name}: No data to import")
            return False
        
        print(f"  [INFO] Loaded {len(data)} documents")
        
        # Step 2: Clear existing documents if requested
        if clear_existing:
            print(f"  [INFO] Clearing existing documents in {collection_name}...")
            result = collection.delete_many({})
            print(f"  [INFO] Deleted {result.deleted_count} existing documents")
        
        # Step 3: Insert new documents
        print(f"  [INFO] Inserting {len(data)} documents...")
        result = collection.insert_many(data)
        print(f"  [PASS] {collection_name}: Inserted {len(result.inserted_ids)} documents")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] {collection_name}: Error - {e}")
        import traceback
        traceback.print_exc()
        return False


def update_documents_by_id(client, db_name, collection_name, file_path):
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
        # Load the new data
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
    """Create or update indexes for the documents collection."""
    print("Creating/updating indexes...")
    
    try:
        # Remove old indexes that reference removed fields
        try:
            db.documents.drop_index("company_id_1_type_1_period_1_date_-1")
            print("  [INFO] Dropped old index: company_id_1_type_1_period_1_date_-1")
        except:
            pass  # Index might not exist
        
        # Create new indexes based on the new structure
        db.documents.create_index("category")
        print("  [PASS] documents.category")
        
        db.documents.create_index([("category", 1), ("date_received", -1)])
        print("  [PASS] documents (category, date_received)")
        
        db.documents.create_index("date_received")
        print("  [PASS] documents.date_received")
        
        db.documents.create_index("created_at")
        print("  [PASS] documents.created_at")
        
        print("[PASS] All indexes created successfully")
        
    except Exception as e:
        print(f"  [FAIL] Error creating indexes: {e}")


def main():
    """Main function to update the database."""
    print("=" * 60)
    print("MongoDB Database Update Script")
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
    
    # Step 3: Update documents collection
    print("Step 2: Updating documents collection...")
    base_path = Path(__file__).parent
    profile_full_path = base_path / profile_path
    documents_file = profile_full_path / 'documents.json'
    
    # Choose update method:
    # Option 1: Clear and re-insert (recommended for structure changes)
    # Option 2: Update by ID (preserves other documents)
    
    USE_CLEAR_AND_INSERT = True  # Set to False to use update_by_id method
    
    if USE_CLEAR_AND_INSERT:
        success = update_documents_collection(
            client, 
            database_name, 
            'documents', 
            str(documents_file),
            clear_existing=True
        )
    else:
        success = update_documents_by_id(
            client,
            database_name,
            'documents',
            str(documents_file)
        )
    
    if not success:
        print("[FAIL] Failed to update documents collection")
        client.close()
        return
    
    print()
    
    # Step 4: Create/update indexes
    print("Step 3: Creating/updating indexes...")
    db = client[database_name]
    create_indexes(db)
    
    print()
    
    # Step 5: Verify
    print("Step 4: Verifying update...")
    collection = db['documents']
    count = collection.count_documents({})
    print(f"[PASS] Documents collection now contains {count} documents")
    
    # Show a sample document structure
    sample = collection.find_one({})
    if sample:
        print(f"[INFO] Sample document structure verified")
        print(f"  - Has _id: {'_id' in sample}")
        print(f"  - Has category: {'category' in sample}")
        print(f"  - Has deadlines: {'deadlines' in sample}")
        print(f"  - Has pending: {'pending' in sample}")
        print(f"  - Has created_at: {'created_at' in sample}")
    
    print()
    print("=" * 60)
    print("[PASS] Database update complete!")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    main()

