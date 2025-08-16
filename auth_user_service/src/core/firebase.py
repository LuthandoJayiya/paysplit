import firebase_admin
from firebase_admin import credentials, auth, firestore
from .config import settings

# Only initialize once
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.firebase_credentials)
    firebase_admin.initialize_app(cred)

# Optional helper functions
def verify_id_token(id_token: str):
    """Verify Firebase ID token and return decoded claims."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid Firebase ID token: {str(e)}")

