"""Authentication router for user login and token management."""

import logging
from fastapi import APIRouter, HTTPException, status
from app.utils.auth import (
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RegisterRequest,
    TokenResponse,
    authenticate_user,
    create_token_response,
    request_mobile_otp,
    register_user,
    verify_mobile_otp,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post(
    "/otp/request",
    status_code=status.HTTP_200_OK,
    summary="Request mobile OTP",
    description="Send a mobile OTP for trust verification and rewards",
)
async def request_otp(request: OTPRequest) -> dict:
    """Request a mobile OTP."""
    try:
        return await request_mobile_otp(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send OTP",
        )


@router.post(
    "/otp/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify mobile OTP",
    description="Verify a mobile OTP and mark the citizen as verified",
)
async def verify_otp(request: OTPVerifyRequest) -> dict:
    """Verify a mobile OTP."""
    try:
        return await verify_mobile_otp(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify OTP",
        )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Create a citizen or official account and return a JWT access token",
)
async def register(request: RegisterRequest) -> TokenResponse:
    """Register a database-backed user account."""
    try:
        user = await register_user(request)

        token_response = create_token_response(
            user_id=user.get("user_id"),
            user_type=user.get("user_type"),
            email=user.get("email"),
        )

        logger.info(f"User registered: {user.get('email')}")
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT access token",
)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Login endpoint for citizens and officials.

    Args:
        request: Login credentials (username/email and password)

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        user = await authenticate_user(request.username, request.password)

        if not user:
            logger.warning(f"Failed login attempt for: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        # Create token response
        token_response = create_token_response(
            user_id=user.get("user_id"),
            user_type=user.get("user_type"),
            email=request.username,
        )

        logger.info(f"User logged in: {request.username}")
        return token_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
        )


@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify token",
    description="Verify if a JWT token is valid",
)
async def verify_token(token: str) -> dict:
    """
    Verify if a JWT token is valid.

    Args:
        token: JWT token to verify

    Returns:
        Token validity information
    """
    try:
        from app.utils.auth import verify_token

        payload = verify_token(token)

        return {
            "valid": True,
            "user_id": payload.sub,
            "user_type": payload.user_type,
            "email": payload.email,
            "message": "Token is valid",
        }

    except HTTPException as e:
        return {
            "valid": False,
            "message": str(e.detail),
        }
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return {
            "valid": False,
            "message": "Error verifying token",
        }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh token",
    description="Refresh an expired or expiring JWT token",
)
async def refresh_token(token: str) -> TokenResponse:
    """
    Refresh a JWT token.

    Args:
        token: Current JWT token

    Returns:
        TokenResponse with new JWT access token
    """
    try:
        from app.utils.auth import verify_token

        payload = verify_token(token)

        # Create new token
        token_response = create_token_response(
            user_id=payload.sub,
            user_type=payload.user_type,
            email=payload.email,
        )

        logger.info(f"Token refreshed for user: {payload.sub}")
        return token_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token",
        )
