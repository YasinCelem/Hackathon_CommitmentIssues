"""
DataStorage Module - MongoDB connection and data operations

This module handles all database connections and data storage/retrieval operations.
It provides services for:
- Users (authentication, CRUD)
- Documents (CRUD with filtering)
- General data (CRUD)
"""

from .db import get_db, get_client
from .services import (
    list_all_users,
    find_user_by_id,
    find_user_by_username,
    find_user_by_email,
    register_user,
    login_user,
    update_user,
    delete_user,
    list_all_data,
    create_data,
    list_documents,
    find_document_by_id,
    create_document,
    update_document,
    delete_document
)

__all__ = [
    'get_db',
    'get_client',
    'list_all_users',
    'find_user_by_id',
    'find_user_by_username',
    'find_user_by_email',
    'register_user',
    'login_user',
    'update_user',
    'delete_user',
    'list_all_data',
    'create_data',
    'list_documents',
    'find_document_by_id',
    'create_document',
    'update_document',
    'delete_document'
]

