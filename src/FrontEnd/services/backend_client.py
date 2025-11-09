import os
import requests
from typing import Optional, Dict, List

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")

class BackendClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_data(self, db_name: Optional[str] = None) -> List[Dict]:
        params = {}
        if db_name:
            params["db_name"] = db_name
        result = self._request("GET", "/api/data/", params=params if params else None)
        return result if result else []
    
    def create_data(self, data: Dict, db_name: Optional[str] = None) -> Optional[Dict]:
        params = {}
        if db_name:
            params["db_name"] = db_name
        return self._request("POST", "/api/data/", json=data, params=params if params else None)
    
    def get_documents(self, category: Optional[str] = None, user_id: Optional[str] = None, db_name: Optional[str] = None) -> List[Dict]:
        params = {}
        if category:
            params["category"] = category
        if user_id:
            params["user_id"] = user_id
        if db_name:
            params["db_name"] = db_name
        result = self._request("GET", "/api/docs/", params=params if params else None)
        return result if result else []
    
    def create_document(self, data: Dict, db_name: Optional[str] = None) -> Optional[Dict]:
        # Make a copy to avoid modifying the original dict
        data_copy = data.copy()
        user_id = data_copy.pop("user_id", None)
        params = {}
        if user_id:
            params["user_id"] = user_id
        if db_name:
            params["db_name"] = db_name
        return self._request("POST", "/api/docs/", json=data_copy, params=params if params else None)
    
    def update_document(self, doc_id: str, data: Dict, db_name: Optional[str] = None) -> Optional[Dict]:
        params = {}
        if db_name:
            params["db_name"] = db_name
        return self._request("PUT", f"/api/docs/{doc_id}", json=data, params=params if params else None)
    
    def delete_document(self, doc_id: str, db_name: Optional[str] = None) -> Optional[Dict]:
        params = {}
        if db_name:
            params["db_name"] = db_name
        return self._request("DELETE", f"/api/docs/{doc_id}", params=params if params else None)
    
    def register_user(self, data: Dict) -> Optional[Dict]:
        return self._request("POST", "/api/users/register", json=data)
    
    def login_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        return self._request("POST", "/api/users/login", json={
            "username_or_email": username_or_email,
            "password": password
        })
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        return self._request("GET", f"/api/users/{user_id}")
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        return self._request("GET", f"/api/users/{username}/profile")

backend_client = BackendClient()

