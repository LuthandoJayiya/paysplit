import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from firebase_admin import firestore
from src.models.user import UserResponse

logger = logging.getLogger(__name__)

class UserService:
    """Manages user profiles in Firestore."""

    def __init__(self):
        # Initialize Firestore client
        self.db = firestore.client()
        self.collection_name = "users"

    async def create_user_profile(self, profile: UserResponse) -> Dict[str, Any]:
        """Create a new user profile in Firestore."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(profile.uid)
            profile_data = profile.dict()
            profile_data["updated_at"] = datetime.utcnow().isoformat()
            
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: doc_ref.set(profile_data)
            )
            
            logger.info(f"User profile created in Firestore: {profile.uid}")
            return profile_data
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise ValueError("Failed to create user profile")

    def get_user_profile(self, uid: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user profile by UID."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(uid)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            return doc.to_dict()
        except Exception as e:
            logger.error(f"Failed to fetch user profile {uid}: {e}")
            raise ValueError("Failed to get user profile")

    def update_user_profile(self, uid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields of a user profile."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(uid)
            updates["updated_at"] = datetime.utcnow().isoformat()
            doc_ref.update(updates)
            logger.info(f"User profile updated: {uid}")
            updated_doc = doc_ref.get()
            return updated_doc.to_dict()
        except Exception as e:
            logger.error(f"Failed to update user profile {uid}: {e}")
            raise ValueError("Failed to update user profile")

    def deactivate_user(self, uid: str) -> bool:
        """Deactivate a user profile (soft delete)."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(uid)
            doc_ref.update({
                "is_active": False,
                "updated_at": datetime.utcnow().isoformat()
            })
            logger.info(f"User profile deactivated: {uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate user {uid}: {e}")
            raise ValueError("Failed to deactivate user")

# Singleton instance
user_service = UserService()
