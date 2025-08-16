from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


# -----------------------------
# REQUEST MODELS
# -----------------------------
class UserSignupRequest(BaseModel):
    """Data required when a user signs up"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone_number: Optional[str] = Field(None)

    @validator("password")
    def strong_password(cls, value: str):
        """Ensure password has uppercase, lowercase, digit and special character"""
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

    @validator("display_name")
    def name_only_letters(cls, value: Optional[str]):
        """Ensure display_name only has letters/spaces"""
        if value and not re.match(r"^[a-zA-Z\s]+$", value):
            raise ValueError("Display name can only contain letters and spaces")
        return value


class UserLoginRequest(BaseModel):
    """Data required when a user logs in"""
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


# -----------------------------
# RESPONSE MODELS
# -----------------------------
class UserResponse(BaseModel):
    """Response after successful signup/login"""
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[str] = None
    role: str = "owner"
    updated_at: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error format"""
    error: str
    message: str
    details: Optional[dict] = None


# -----------------------------
# PROFILE MODEL
# -----------------------------
class UserProfile(BaseModel):
    """User profile stored in Firestore"""
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = "owner" #default role if role is not provided
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # bio: Optional[str] = None   # extra field for future use
    # avatar_url: Optional[str] = None  # store profile picture
