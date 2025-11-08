from ..db import get_db
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


# ---------- Helpers ----------

def _users():
    """Return Mongo collection for users."""
    return get_db()["users"]


# ---------- CRUD ----------

def list_all() -> list[dict]:
    """List all users (sorted newest first)."""
    return list(_users().find().sort("_id", -1))


def find_by_id(user_id: str) -> Optional[dict]:
    """Find a user by ObjectId string."""
    try:
        return _users().find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def find_by_username(username: str) -> Optional[dict]:
    """Find user by username."""
    return _users().find_one({"username": username})


def find_by_email(email: str) -> Optional[dict]:
    """Find user by email."""
    return _users().find_one({"email": email})


def register(document: dict) -> Optional[str]:
    """
    Register a new user.
    Expected keys: username, email, password
    """
    username = document.get("username")
    email = document.get("email")
    password = document.get("password")

    # --- Validation ---
    if not username or not email or not password:
        raise ValueError("Missing username, email, or password.")

    # --- Check duplicates ---
    if find_by_username(username):
        raise ValueError("Username already exists.")
    if find_by_email(email):
        raise ValueError("Email already registered.")

    # --- Hash password ---
    document["password"] = generate_password_hash(password)

    res = _users().insert_one(document)
    return str(res.inserted_id)


def login(username_or_email: str, password: str) -> Optional[dict]:
    """
    Verify credentials.
    Returns user dict if success, None otherwise.
    """
    user = find_by_username(username_or_email) or find_by_email(username_or_email)
    if not user:
        return None

    if check_password_hash(user["password"], password):
        return user
    return None


def update(user_id: str, updates: dict) -> bool:
    """Update user info."""
    res = _users().update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return res.modified_count > 0


def delete(user_id: str) -> bool:
    """Delete user by ID."""
    res = _users().delete_one({"_id": ObjectId(user_id)})
    return res.deleted_count > 0
