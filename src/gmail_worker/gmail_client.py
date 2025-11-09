from googleapiclient.discovery import build
from .auth import load_creds

def gmail_service():
    return build("gmail", "v1", credentials=load_creds(), cache_discovery=False)
