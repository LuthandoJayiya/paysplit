import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Path to your Firebase service account key
FIREBASE_KEY_PATH = os.getenv("FIREBASE_CREDENTIALS", "paysplit-service-firebase-adminsdk-fbsvc-0a5a44a8e7.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    if os.path.exists(FIREBASE_KEY_PATH):
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")
    else:
        print("Firebase credentials not found, using mock database")
        # Mock implementation for testing
        class MockDB:
            def collection(self, name):
                return MockCollection()
        
        class MockCollection:
            def document(self, doc_id=None):
                return MockDocument(doc_id)
            
            def add(self, data):
                return "mock-doc-id", data
            
            def stream(self):
                return []
        
        class MockDocument:
            def __init__(self, doc_id=None):
                self.id = doc_id or "mock-doc-id"
            
            def set(self, data):
                return self.id
            
            def get(self):
                return MockDocumentSnapshot()
            
            def delete(self):
                return True
        
        class MockDocumentSnapshot:
            def exists(self):
                return False
            
            def to_dict(self):
                return {}
        
        db = MockDB()
        firebase_auth = None

db = firestore.client() if os.path.exists(FIREBASE_KEY_PATH) else MockDB()
firebase_auth = auth if os.path.exists(FIREBASE_KEY_PATH) else None
