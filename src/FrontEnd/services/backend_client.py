import requests
import os
from typing import Optional, Dict, List, Any

# Backend API base URL - defaults to localhost:5001
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")


class BackendClient:
    """Client for communicating with the backend API"""
    
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Any]:
        """Make an HTTP request to the backend API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=5
            )
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def login_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        """Login a user"""
        return self._make_request(
            "POST",
            "/api/users/login",
            data={
                "username_or_email": username_or_email,
                "password": password
            }
        )
    
    def register_user(self, user_data: Dict) -> Optional[Dict]:
        """Register a new user"""
        return self._make_request(
            "POST",
            "/api/users/register",
            data=user_data
        )
    
    def get_documents(
        self, 
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> List[Dict]:
        """Get all documents, optionally filtered by category and user_id"""
        params = {}
        if category:
            params["category"] = category
        if user_id:
            params["user_id"] = user_id
        if db_name:
            params["db_name"] = db_name
        
        result = self._make_request("GET", "/api/docs/", params=params)
        return result if result is not None else []
    
    def create_document(self, data: Dict, db_name: Optional[str] = None) -> Optional[Dict]:
        """Create a new document"""
        params = {}
        if db_name:
            params["db_name"] = db_name
        
        return self._make_request(
            "POST",
            "/api/docs/",
            data=data,
            params=params
        )
    
    def update_document(
        self, 
        doc_id: str, 
        data: Dict, 
        db_name: Optional[str] = None
    ) -> Optional[Dict]:
        """Update an existing document"""
        params = {}
        if db_name:
            params["db_name"] = db_name
        
        return self._make_request(
            "PUT",
            f"/api/docs/{doc_id}",
            data=data,
            params=params
        )
    
    def delete_document(self, doc_id: str, db_name: Optional[str] = None) -> Optional[Dict]:
        """Delete a document"""
        params = {}
        if db_name:
            params["db_name"] = db_name
        
        return self._make_request(
            "DELETE",
            f"/api/docs/{doc_id}",
            params=params
        )
    
    def get_data(self, db_name: Optional[str] = None) -> List[Dict]:
        """Get all data records"""
        params = {}
        if db_name:
            params["db_name"] = db_name
        
        result = self._make_request("GET", "/api/data/", params=params)
        return result if result is not None else []
    
    def create_data(self, data: Dict, db_name: Optional[str] = None) -> Optional[Dict]:
        """Create a new data record"""
        params = {}
        if db_name:
            params["db_name"] = db_name
        
        return self._make_request(
            "POST",
            "/api/data/",
            data=data,
            params=params
        )


# Create a singleton instance
backend_client = BackendClient()

