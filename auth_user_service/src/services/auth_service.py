import httpx
import logging
import asyncio
from typing import Dict, Any, Optional
from firebase_admin import auth
from pydantic import EmailStr
from src.models.user import UserResponse
from src.services.user_service import user_service
from src.core.security import create_access_token
from src.core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling Firebase authentication operations."""
    FIREBASE_REST_SIGNIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements."""
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if len(password) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return True
    
    @staticmethod
    async def signup_user(
        email: EmailStr, 
        password: str, 
        display_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        role="owner",
        send_email_verification: bool = True
    ) -> UserResponse:
        """
        Create a new user with email and password in Firebase.
        
        Args:
            email: User's email address
            password: User's password (will be validated)
            display_name: Optional display name
            phone_number: Optional phone number
            send_email_verification: Whether to send verification email
            
        Returns:
            UserResponse with user details
            
        Raises:
            ValueError: If user creation fails
        """
        try:
            AuthService.validate_password_strength(password)
            
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: auth.get_user_by_email(email)
                )
                raise ValueError("Email address is already in use")
            except auth.UserNotFoundError:
                pass 
            
            user_create_params = {
                'email': email,
                'password': password,
                'email_verified': False
            }
            
            if display_name:
                user_create_params['display_name'] = display_name
                
            if phone_number:
                user_create_params['phone_number'] = phone_number
            
            user = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: auth.create_user(**user_create_params)
            )
            
            # Send email verification if requested
            if send_email_verification:
                try:
                    link = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: auth.generate_email_verification_link(email)
                    )
                    logger.info(f"Email verification link generated for {email}")
                    # TODO: Send email with verification link
                except Exception as e:
                    logger.warning(f"Failed to generate email verification link: {str(e)}")
            
            # Create user response
            user_response = UserResponse(
                uid=user.uid,
                email=user.email,
                display_name=user.display_name,
                phone_number=user.phone_number,
                email_verified=user.email_verified,
                role=role,
                created_at=str(user.user_metadata.creation_timestamp) if user.user_metadata.creation_timestamp else None,
                updated_at=str(user.user_metadata.last_refresh_timestamp) if user.user_metadata.last_refresh_timestamp else None
            )
            
            # Store user profile in database
            await user_service.create_user_profile(user_response)
            
            return user_response
            
        except ValueError as e:
            raise e
        except Exception as e:
            error_msg = str(e).lower()
            if "email" in error_msg and "invalid" in error_msg:
                raise ValueError("Invalid email address format")
            elif "password" in error_msg and ("weak" in error_msg or "strength" in error_msg):
                raise ValueError("Password is too weak")
            elif "phone" in error_msg and "exists" in error_msg:
                raise ValueError("Phone number is already in use")
            elif "email" in error_msg and "exists" in error_msg:
                raise ValueError("Email address is already in use")
            else:
                logger.error(f"Error creating user: {str(e)}")
                raise ValueError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def get_user_by_uid(uid: str) -> Dict[str, Any]:
        """Get user details by UID."""
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'phone_number': user.phone_number,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'created_at': str(user.user_metadata.creation_timestamp),
                'updated_at': str(user.user_metadata.last_refresh_timestamp)
            }
        except auth.UserNotFoundError:
            raise ValueError("User not found")
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise ValueError(f"Failed to get user: {str(e)}")
    
    @staticmethod
    def delete_user(uid: str) -> bool:
        """Delete a user by UID."""
        try:
            auth.delete_user(uid)
            logger.info(f"User {uid} deleted successfully")
            return True
        except auth.UserNotFoundError:
            raise ValueError("User not found")
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise ValueError(f"Failed to delete user: {str(e)}")
        
    @staticmethod
    async def login_user(email: str, password: str) -> dict:
        """
        Authenticate user via Firebase REST API and return JWT access token.
        """
        try:
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            params = {"key": settings.firebase_api_key}

            async with httpx.AsyncClient() as client:
                resp = await client.post(AuthService.FIREBASE_REST_SIGNIN_URL, json=payload, params=params)
                resp_data = resp.json()

            if resp.status_code != 200:
                raise ValueError(resp_data.get("error", {}).get("message", "Invalid credentials"))

            # Extract Firebase user info
            uid = resp_data["localId"]
            email_verified = resp_data.get("emailVerified", False)
            id_token = resp_data["idToken"]

            # Optionally i can fetch more user info from Firebase Admin
            from firebase_admin import auth
            user = auth.get_user(uid)

            # Create your own JWT token for your API
            token_data = {"sub": uid, "email": user.email, "roles": ["user"]}
            access_token = create_access_token(token_data)

            return {
                "user": UserResponse(
                    uid=user.uid,
                    email=user.email,
                    display_name=user.display_name,
                    phone_number=user.phone_number,
                    email_verified=user.email_verified
                ),
                "access_token": access_token,
                "token_type": "bearer",
                "firebase_id_token": id_token
            }

        except Exception as e:
            raise ValueError(f"Login failed: {str(e)}")


def signup_user(email: EmailStr, password: str):
    """Legacy function for backward compatibility."""
    return AuthService.signup_user(email=email, password=password)

