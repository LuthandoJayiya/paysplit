import logging
from fastapi import APIRouter, HTTPException, Request
from src.models.user import UserSignupRequest, UserResponse, ErrorResponse
from src.services.auth_service import AuthService
from src.models.user import UserLoginRequest


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/signup",
    response_model=UserResponse,
    summary="Signup/Register a new user",
    description="Create a new user in Firebase Authentication and Firestore.",
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def signup(
    request: Request,
    user: UserSignupRequest,
    send_email_verification: bool = True
):
    """
    Create a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (min 6 chars, uppercase, lowercase, digit, special char)
    - **display_name**: Optional display name (2-50 chars, letters and spaces only)
    - **phone_number**: Optional phone number in international format
    
    Returns user details including UID and email verification status.
    """
    try:
        logger.info(f"Signup attempt for email: {user.email} from IP: {request.client.host}")

        result = await AuthService.signup_user(
            email=user.email,
            password=user.password,
            display_name=user.display_name,
            phone_number=user.phone_number,
            send_email_verification=send_email_verification
        )

        logger.info(f"User created successfully: {result.uid}")
        return result

    except ValueError as e:
        logger.warning(f"Signup validation error: {str(e)}")
        if "already in use" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=ErrorResponse(
                    error="USER_EXISTS",
                    message=str(e)
                ).dict()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="VALIDATION_ERROR",
                    message=str(e)
                ).dict()
            )
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="An unexpected error occurred. Please try again later."
            ).dict()
        )


@router.post(
    "/login",
    summary="Login user",
    description="Authenticate user and return JWT token",
)
async def login(login_data: UserLoginRequest):
    """
    Login user with email and password, returning API JWT and Firebase ID token.
    """
    try:
        result = await AuthService.login_user(email=login_data.email, password=login_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
