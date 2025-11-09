import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.DataStorage.db import get_client, username_to_db_name, get_user_db
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


def _get_user_collection(db_name: Optional[str] = None):
    """Return Mongo collection for users in specified database."""
    from src.DataStorage.db import get_db
    db = get_db(db_name) if db_name else get_db()
    return db["users"]


def find_user_in_database(db_name: str, username: str = None, email: str = None) -> Optional[dict]:
    """Find user in a specific database by username or email."""
    try:
        db = get_client()[db_name]
        users_col = db["users"]
        
        if username:
            user = users_col.find_one({"Username": username}) or users_col.find_one({"username": username})
            if user:
                return user
        
        if email:
            user = users_col.find_one({"email": email})
            if user:
                return user
    except Exception:
        pass
    return None


def find_user_by_username(username: str) -> Optional[dict]:
    """
    Find user by username across all databases.
    First checks Zane_Dima database, then user's own database, then other databases.
    """
    if not username:
        return None
    
    user = find_user_in_database("Zane_Dima", username=username)
    if user:
        return user
    
    db_name = username_to_db_name(username)
    if db_name != "Zane_Dima":
        user = find_user_in_database(db_name, username=username)
        if user:
            return user
    
    db_list = get_client().list_database_names()
    for db_name in db_list:
        if db_name not in ["admin", "local", "config", "Zane_Dima"]:
            user = find_user_in_database(db_name, username=username)
            if user:
                return user
    
    return None


def find_user_by_email(email: str) -> Optional[dict]:
    """
    Find user by email across all databases.
    First checks Zane_Dima database, then other databases.
    """
    if not email:
        return None
    
    user = find_user_in_database("Zane_Dima", email=email)
    if user:
        return user
    
    db_list = get_client().list_database_names()
    for db_name in db_list:
        if db_name not in ["admin", "local", "config", "Zane_Dima"]:
            user = find_user_in_database(db_name, email=email)
            if user:
                return user
    
    return None


def login_user(username_or_email: str, password: str) -> Optional[dict]:
    """
    Verify credentials across all databases.
    Returns user dict with database_name set to Zane_Dima if success, None otherwise.
    """
    user = find_user_by_username(username_or_email) or find_user_by_email(username_or_email)
    if not user:
        return None
    
    user_password = user.get("password") or user.get("Password")
    if not user_password:
        return None
    
    if user_password == password:
        username = user.get("Username") or user.get("username")
        if username:
            user["database_name"] = "Zane_Dima"
            user["username"] = username
        return user
    
    try:
        from werkzeug.security import check_password_hash
        if check_password_hash(user_password, password):
            username = user.get("Username") or user.get("username")
            if username:
                user["database_name"] = "Zane_Dima"
                user["username"] = username
            return user
    except Exception:
        pass
    
    return None


def find_user_by_id(user_id: str, db_name: Optional[str] = None) -> Optional[dict]:
    """Find a user by ObjectId string in specified database."""
    try:
        users_col = _get_user_collection(db_name)
        return users_col.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def list_all_users() -> list[dict]:
    """List all users from default database (sorted newest first)."""
    return list(_get_user_collection().find().sort("_id", -1))


def register_user(document: dict) -> Optional[str]:
    """
    Register a new user in Zane_Dima database.
    Expected keys: username, email, password
    """
    username = document.get("username")
    email = document.get("email")
    password = document.get("password")

    if not username or not email or not password:
        raise ValueError("Missing username, email, or password.")

    if find_user_by_username(username):
        raise ValueError("Username already exists.")
    if find_user_by_email(email):
        raise ValueError("Email already registered.")

    db = get_db("Zane_Dima")
    users_col = db["users"]
    
    document["password"] = generate_password_hash(password)
    document["username"] = username
    document["Username"] = username

    res = users_col.insert_one(document)
    return str(res.inserted_id)


def update_user(user_id: str, updates: dict, db_name: Optional[str] = None) -> bool:
    """Update user info in specified database."""
    try:
        users_col = _get_user_collection(db_name)
        res = users_col.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        return res.modified_count > 0
    except Exception:
        return False


def delete_user(user_id: str, db_name: Optional[str] = None) -> bool:
    """Delete user by ID from specified database."""
    try:
        users_col = _get_user_collection(db_name)
        res = users_col.delete_one({"_id": ObjectId(user_id)})
        return res.deleted_count > 0
    except Exception:
        return False

