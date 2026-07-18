"""Authentication and authorization utilities."""

import logging
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from app.config import settings
from app.utils.database import get_database, normalize_mongo_document
from app.utils.notifications import send_sms

logger = logging.getLogger(__name__)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str = Field(..., description="Subject (user ID)")
    user_type: str = Field(..., description="Type: citizen or official")
    email: Optional[str] = Field(None, description="User email")
    exp: Optional[datetime] = Field(None, description="Expiration time")
    iat: Optional[datetime] = Field(None, description="Issued at")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "sub": "user_123",
                "user_type": "citizen",
                "email": "user@example.com",
            }
        }


class LoginRequest(BaseModel):
    """Login request."""

    username: str = Field(..., description="Username or email", min_length=3)
    password: str = Field(..., description="Password", min_length=6)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "username": "john@example.com",
                "password": "secure_password_123",
            }
        }


class RegisterRequest(BaseModel):
    """User registration request."""

    name: str = Field(..., description="Full name", min_length=2)
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password", min_length=6)
    user_type: str = Field(default="citizen", description="citizen or official")
    phone: Optional[str] = Field(None, description="Phone number")
    ward_id: Optional[str] = Field(None, description="Ward identifier")
    department: Optional[str] = Field(None, description="Official department")
    designation: Optional[str] = Field(None, description="Official designation")


class OTPRequest(BaseModel):
    """Request mobile OTP verification."""

    user_id: str = Field(..., description="Citizen user ID")
    phone: str = Field(..., description="Mobile phone number")
    purpose: str = Field(default="complaint_trust", description="OTP purpose")


class OTPVerifyRequest(BaseModel):
    """Verify mobile OTP."""

    user_id: str = Field(..., description="Citizen user ID")
    phone: str = Field(..., description="Mobile phone number")
    otp_code: str = Field(..., min_length=4, max_length=8, description="OTP code")
    purpose: str = Field(default="complaint_trust", description="OTP purpose")


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str = Field(..., description="User ID")
    user_type: str = Field(..., description="User type: citizen or official")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_id": "user_123",
                "user_type": "citizen",
            }
        }


def create_access_token(
    user_id: str,
    user_type: str,
    email: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User identifier
        user_type: Type of user (citizen or official)
        email: Optional user email
        expires_delta: Optional custom expiration time

    Returns:
        JWT token string
    """
    try:
        if not user_id:
            raise ValueError("user_id is required")
        if not user_type:
            raise ValueError("user_type is required")

        if expires_delta is None:
            expires_delta = timedelta(
                minutes=settings.access_token_expire_minutes
            )

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": user_id,
            "user_type": user_type,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        logger.info(f"Created access token for user: {user_id} ({user_type})")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create token",
        )


def verify_token(token: str) -> TokenPayload:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")
        user_type = payload.get("user_type")

        if user_id is None or user_type is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )

        token_payload = TokenPayload(
            sub=user_id,
            user_type=user_type,
            email=payload.get("email"),
        )

        return token_payload

    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials) -> TokenPayload:
    """
    Get current user from Bearer token.

    Args:
        credentials: HTTPAuthCredentials from FastAPI security

    Returns:
        Token payload with user information

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    return verify_token(token)


def create_token_response(
    user_id: str,
    user_type: str,
    email: Optional[str] = None,
) -> TokenResponse:
    """
    Create a token response with all necessary fields.

    Args:
        user_id: User identifier
        user_type: Type of user
        email: Optional user email

    Returns:
        TokenResponse with access token and metadata
    """
    access_token = create_access_token(
        user_id=user_id,
        user_type=user_type,
        email=email,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id,
        user_type=user_type,
    )


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a hash."""
    return pwd_context.verify(plain_password, password_hash)


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user against MongoDB.

    Args:
        username: Username or email
        password: Plain text password

    Returns:
        User information if authenticated, None otherwise
    """
    db = await get_database()
    email = username.strip().lower()

    for collection_name, user_type in (("citizens", "citizen"), ("officials", "official")):
        user = await db[collection_name].find_one({"email": email, "account_status": "active"})
        if not user:
            continue

        user = normalize_mongo_document(user)
        password_hash = user.get("password_hash")
        if password_hash and verify_password(password, password_hash):
            await db[collection_name].update_one(
                {"email": email},
                {"$set": {"last_login": datetime.utcnow()}},
            )
            logger.info(f"User authenticated: {email}")
            return {
                **user,
                "user_type": user.get("user_type", user_type),
            }

    logger.warning(f"Failed authentication attempt for: {email}")
    return None


async def register_user(request: RegisterRequest) -> Dict[str, Any]:
    """Create a citizen or official account in MongoDB."""
    db = await get_database()
    email = request.email.strip().lower()
    user_type = request.user_type.strip().lower()

    if user_type not in {"citizen", "official"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_type must be citizen or official",
        )

    existing_citizen = await db["citizens"].find_one({"email": email})
    existing_official = await db["officials"].find_one({"email": email})
    if existing_citizen or existing_official:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    now = datetime.utcnow()
    prefix = "CITI" if user_type == "citizen" else "OFF"
    user_id = f"{prefix}_{int(now.timestamp() * 1000)}"

    if user_type == "citizen":
        document = {
            "user_id": user_id,
            "name": request.name,
            "email": email,
            "password_hash": hash_password(request.password),
            "user_type": "citizen",
            "phone": request.phone,
            "ward_id": request.ward_id,
            "verified": False,
            "account_status": "active",
            "complaints_submitted": 0,
            "complaints_resolved": 0,
            "average_rating": 0,
            "badges": [],
            "preferences": {},
            "notification_settings": {"email": True, "sms": False, "push": True},
            "impact_score": 0,
            "created_at": now,
            "updated_at": now,
        }
        collection_name = "citizens"
    else:
        document = {
            "user_id": user_id,
            "name": request.name,
            "email": email,
            "password_hash": hash_password(request.password),
            "user_type": "official",
            "phone": request.phone or "",
            "designation": request.designation or "Municipal Official",
            "department": request.department or "General_Services",
            "ward_id": request.ward_id or "unassigned",
            "authority_level": "field_staff",
            "office_address": "",
            "office_latitude": 0.0,
            "office_longitude": 0.0,
            "verified": False,
            "account_status": "active",
            "complaints_assigned": 0,
            "complaints_resolved": 0,
            "average_resolution_days": 0,
            "performance_rating": 0,
            "escalations_received": 0,
            "escalations_handled": 0,
            "availability_status": "available",
            "shift_start_hour": 9,
            "shift_end_hour": 17,
            "response_time_minutes": 60,
            "specializations": [],
            "team_members": [],
            "notification_preferences": {"email": True, "sms": False},
            "metadata": {},
            "created_at": now,
            "updated_at": now,
        }
        collection_name = "officials"

    result = await db[collection_name].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def request_mobile_otp(request: OTPRequest) -> Dict[str, Any]:
    """Create and send a short-lived mobile OTP."""
    db = await get_database()
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    await db["otp_verifications"].update_one(
        {
            "user_id": request.user_id,
            "phone": request.phone,
            "purpose": request.purpose,
            "verified": False,
        },
        {
            "$set": {
                "otp_hash": hash_password(otp_code),
                "expires_at": expires_at,
                "attempts": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    await send_sms(
        request.phone,
        f"Your NagarSeva verification code is {otp_code}. It expires in 10 minutes.",
    )
    return {
        "status": "sent",
        "phone": request.phone,
        "purpose": request.purpose,
        "expires_at": expires_at.isoformat(),
    }


async def verify_mobile_otp(request: OTPVerifyRequest) -> Dict[str, Any]:
    """Verify a mobile OTP and mark the citizen as phone verified."""
    db = await get_database()
    record = await db["otp_verifications"].find_one(
        {
            "user_id": request.user_id,
            "phone": request.phone,
            "purpose": request.purpose,
            "verified": False,
        },
        sort=[("created_at", -1)],
    )
    record = normalize_mongo_document(record)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found")

    if record.get("expires_at") and record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    if record.get("attempts", 0) >= 5:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many OTP attempts")

    if not verify_password(request.otp_code, record["otp_hash"]):
        await db["otp_verifications"].update_one(
            {"_id": record["_id"]},
            {"$inc": {"attempts": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    await db["otp_verifications"].update_one(
        {"_id": record["_id"]},
        {
            "$set": {
                "verified": True,
                "verified_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        },
    )
    await db["citizens"].update_one(
        {"user_id": request.user_id},
        {
            "$set": {
                "phone": request.phone,
                "phone_verified": True,
                "verified": True,
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return {
        "status": "verified",
        "user_id": request.user_id,
        "phone": request.phone,
        "purpose": request.purpose,
    }
