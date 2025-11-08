import json
import os
from datetime import datetime
from pathlib import Path

STORAGE_DIR = Path(__file__).parent
TRACKER_FILE = STORAGE_DIR / "visit_tracker.json"

def load_visits():
    if not TRACKER_FILE.exists():
        return {"visits": []}
    try:
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"visits": []}

def save_visits(data):
    try:
        with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError:
        pass

def track_visit(endpoint, title, icon):
    data = load_visits()
    visits = data.get("visits", [])
    
    existing = next((v for v in visits if v.get("endpoint") == endpoint), None)
    
    if existing:
        existing["count"] = existing.get("count", 0) + 1
        existing["last_visited"] = datetime.now().isoformat()
    else:
        visits.append({
            "endpoint": endpoint,
            "title": title,
            "icon": icon,
            "count": 1,
            "last_visited": datetime.now().isoformat()
        })
    
    data["visits"] = visits
    save_visits(data)

def get_top_visits(limit=3):
    data = load_visits()
    visits = data.get("visits", [])
    
    if not visits:
        return []
    
    filtered_visits = [v for v in visits if v.get("endpoint") != "frontend.settings"]
    
    if not filtered_visits:
        return []
    
    def sort_key(x):
        count = x.get("count", 0)
        last_visited = x.get("last_visited", "")
        return (count, last_visited)
    
    sorted_visits = sorted(filtered_visits, key=sort_key, reverse=True)
    
    return sorted_visits[:limit]

def get_category_mapping():
    try:
        from ..nav import NAV
    except ImportError:
        from src.FrontEnd.nav import NAV
    
    mapping = {}
    for section in NAV:
        main_endpoint = section.get("endpoint")
        if main_endpoint:
            mapping[main_endpoint] = main_endpoint
            for child in section.get("children", []):
                child_endpoint = child.get("endpoint")
                if child_endpoint:
                    mapping[child_endpoint] = main_endpoint
    return mapping

def get_recent_visits(limit=3):
    data = load_visits()
    visits = data.get("visits", [])
    
    if not visits:
        return []
    
    filtered_visits = [v for v in visits if v.get("endpoint") != "frontend.settings"]
    
    if not filtered_visits:
        return []
    
    category_mapping = get_category_mapping()
    category_data = {}
    
    for visit in filtered_visits:
        endpoint = visit.get("endpoint")
        category_endpoint = category_mapping.get(endpoint)
        
        if not category_endpoint or category_endpoint == "frontend.settings":
            continue
        
        if category_endpoint not in category_data:
            try:
                from ..nav import NAV
            except ImportError:
                from src.FrontEnd.nav import NAV
            category_info = next((s for s in NAV if s.get("endpoint") == category_endpoint), None)
            if category_info:
                category_data[category_endpoint] = {
                    "endpoint": category_endpoint,
                    "title": category_info.get("label"),
                    "icon": category_info.get("icon", "").replace("bi-", ""),
                    "count": 0,
                    "last_visited": ""
                }
        
        if category_endpoint in category_data:
            category_data[category_endpoint]["count"] += visit.get("count", 0)
            visit_time = visit.get("last_visited", "")
            if visit_time > category_data[category_endpoint]["last_visited"]:
                category_data[category_endpoint]["last_visited"] = visit_time
    
    category_list = list(category_data.values())
    
    if not category_list:
        return []
    
    def sort_key(x):
        last_visited = x.get("last_visited", "")
        count = x.get("count", 0)
        return (last_visited, count)
    
    sorted_visits = sorted(category_list, key=sort_key, reverse=True)
    
    return sorted_visits[:limit]

