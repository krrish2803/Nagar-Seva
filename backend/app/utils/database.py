"""Database utilities and MongoDB index setup."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from passlib.context import CryptContext
from pymongo import ASCENDING, DESCENDING, GEOSPHERE
from app.config import settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

_mongo_client: Optional[AsyncIOMotorClient] = None


def _mongo_uri() -> str:
    """Return configured MongoDB URI."""
    return settings.mongodb_url


async def connect_to_mongo() -> AsyncIOMotorClient:
    """Create connection to MongoDB."""
    global _mongo_client

    try:
        if _mongo_client is not None:
            return _mongo_client

        client = AsyncIOMotorClient(_mongo_uri())
        # Verify connection
        await client.admin.command("ping")
        _mongo_client = client
        logger.info("Connected to MongoDB successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection(client: Optional[AsyncIOMotorClient] = None) -> None:
    """Close MongoDB connection."""
    global _mongo_client

    client_to_close = client or _mongo_client
    if client_to_close:
        client_to_close.close()
        if client_to_close is _mongo_client:
            _mongo_client = None
        logger.info("Closed MongoDB connection")


async def get_database() -> AsyncIOMotorDatabase:
    """Get the configured MongoDB database."""
    client = await connect_to_mongo()
    return client[settings.mongodb_database]


def normalize_mongo_document(document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert MongoDB-only values into JSON/Pydantic friendly values."""
    if document is None:
        return None

    normalized = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            normalized[key] = str(value)
        elif isinstance(value, dict):
            normalized[key] = normalize_mongo_document(value)
        elif isinstance(value, list):
            normalized[key] = [
                normalize_mongo_document(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            normalized[key] = value
    return normalized


def to_mongo_document(model_or_dict: Any) -> Dict[str, Any]:
    """Serialize Pydantic models or dictionaries for MongoDB."""
    if hasattr(model_or_dict, "model_dump"):
        data = model_or_dict.model_dump(by_alias=True, mode="python")
    elif hasattr(model_or_dict, "dict"):
        data = model_or_dict.dict(by_alias=True)
    else:
        data = dict(model_or_dict)

    if data.get("_id") is None:
        data.pop("_id", None)
    return data


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Create indexes for MongoDB collections.
    
    This function sets up:
    - Geospatial 2dsphere indexes on location fields
    - Compound indexes for common query patterns
    - TTL indexes for temporary data
    
    Args:
        db: AsyncDatabase instance from motor
    """
    try:
        logger.info("Creating MongoDB indexes...")

        # ==================== COMPLAINTS COLLECTION ====================
        complaints = db["complaints"]

        # Geospatial index on location
        await complaints.create_index(
            [("location_point", GEOSPHERE)],
            name="location_2dsphere",
            sparse=True,
        )
        logger.info("✓ Created geospatial index on complaints.location_point")

        # Compound indexes for common queries
        await complaints.create_index(
            [("status", ASCENDING), ("created_at", DESCENDING)],
            name="status_created_idx",
        )
        logger.info("✓ Created compound index on complaints (status, created_at)")

        await complaints.create_index(
            [("citizen_id", ASCENDING), ("created_at", DESCENDING)],
            name="citizen_created_idx",
        )
        logger.info("✓ Created compound index on complaints (citizen_id, created_at)")

        await complaints.create_index(
            [("classification.issue_type", ASCENDING), ("classification.severity", ASCENDING)],
            name="classification_idx",
        )
        logger.info("✓ Created compound index on complaints classification")

        await complaints.create_index(
            [("trust_score.overall_score", DESCENDING), ("trust_score.recommended_action", ASCENDING)],
            name="trust_score_idx",
            sparse=True,
        )
        logger.info("✓ Created compound index on complaints trust score")

        await complaints.create_index(
            [("location.ward_id", ASCENDING), ("status", ASCENDING)],
            name="ward_status_idx",
        )
        logger.info("✓ Created compound index on complaints (ward_id, status)")

        await complaints.create_index(
            [("assignment.official_id", ASCENDING), ("status", ASCENDING)],
            name="official_status_idx",
        )
        logger.info("✓ Created compound index on complaints (official_id, status)")

        # TTL index for old documents (cleanup after 2 years)
        await complaints.create_index(
            [("created_at", ASCENDING)],
            name="old_complaints_ttl",
            expireAfterSeconds=63072000,  # 2 years
        )
        logger.info("✓ Created TTL index on complaints (2 year expiration)")

        # ==================== OFFICIALS COLLECTION ====================
        officials = db["officials"]

        await officials.create_index(
            [("email", ASCENDING)],
            name="email_idx",
            unique=True,
            sparse=True,
        )
        logger.info("✓ Created unique index on officials.email")

        await officials.create_index(
            [("department", ASCENDING), ("workload", ASCENDING)],
            name="dept_workload_idx",
        )
        logger.info("✓ Created compound index on officials (department, workload)")

        await officials.create_index(
            [("department", ASCENDING), ("ward_id", ASCENDING), ("availability_status", ASCENDING)],
            name="dept_ward_availability_idx",
        )
        logger.info("✓ Created compound index on officials (department, ward, availability)")

        # ==================== CITIZENS COLLECTION ====================
        citizens = db["citizens"]

        await citizens.create_index(
            [("phone", ASCENDING)],
            name="phone_idx",
            unique=True,
            sparse=True,
        )
        logger.info("✓ Created unique index on citizens.phone")

        await citizens.create_index(
            [("email", ASCENDING)],
            name="email_idx",
            unique=True,
            sparse=True,
        )
        logger.info("✓ Created unique index on citizens.email")

        # ==================== WARDS COLLECTION ====================
        wards = db["wards"]

        await wards.create_index(
            [("geometry.coordinates", GEOSPHERE)],
            name="geometry_2dsphere",
            sparse=True,
        )
        logger.info("✓ Created geospatial index on wards.geometry")

        await wards.create_index(
            [("code", ASCENDING)],
            name="ward_code_idx",
            unique=True,
        )
        logger.info("✓ Created unique index on wards.code")

        # ==================== ESCALATIONS COLLECTION ====================
        escalations = db["escalations"]

        await escalations.create_index(
            [("status", ASCENDING), ("escalated_at", DESCENDING)],
            name="status_escalated_idx",
        )
        logger.info("✓ Created compound index on escalations (status, escalated_at)")

        await escalations.create_index(
            [("complaint_id", ASCENDING)],
            name="complaint_id_idx",
        )
        logger.info("✓ Created index on escalations.complaint_id")

        await escalations.create_index(
            [("escalated_to_official_id", ASCENDING), ("status", ASCENDING)],
            name="official_status_escalation_idx",
        )
        logger.info("✓ Created compound index on escalations (official_id, status)")

        # TTL index for resolved escalations (cleanup after 1 year)
        await escalations.create_index(
            [("escalated_at", ASCENDING)],
            name="old_escalations_ttl",
            expireAfterSeconds=31536000,  # 1 year
        )
        logger.info("✓ Created TTL index on escalations (1 year expiration)")

        # ==================== ROUTES COLLECTION ====================
        routes = db["routes"]

        await routes.create_index(
            [("origin", GEOSPHERE), ("destination", GEOSPHERE)],
            name="route_coords_2dsphere",
            sparse=True,
        )
        logger.info("✓ Created geospatial indexes on routes")

        await routes.create_index(
            [("citizen_id", ASCENDING), ("created_at", DESCENDING)],
            name="citizen_route_created_idx",
        )
        logger.info("✓ Created compound index on routes (citizen_id, created_at)")

        # TTL index for old routes (cleanup after 30 days)
        await routes.create_index(
            [("created_at", ASCENDING)],
            name="old_routes_ttl",
            expireAfterSeconds=2592000,  # 30 days
        )
        logger.info("✓ Created TTL index on routes (30 day expiration)")

        # ==================== SAFETY_HEATMAPS COLLECTION ====================
        heatmaps = db["safety_heatmaps"]

        await heatmaps.create_index(
            [("cluster_center", GEOSPHERE)],
            name="cluster_center_2dsphere",
            sparse=True,
        )
        logger.info("✓ Created geospatial index on safety_heatmaps")

        await heatmaps.create_index(
            [("generated_at", DESCENDING)],
            name="generated_at_idx",
        )
        logger.info("✓ Created index on safety_heatmaps.generated_at")

        # TTL index for old heatmaps (cleanup after 90 days)
        await heatmaps.create_index(
            [("generated_at", ASCENDING)],
            name="old_heatmaps_ttl",
            expireAfterSeconds=7776000,  # 90 days
        )
        logger.info("✓ Created TTL index on safety_heatmaps (90 day expiration)")

        # ==================== SAFETY_INCIDENTS COLLECTION ====================
        safety_incidents = db["safety_incidents"]

        await safety_incidents.create_index(
            [("location_point", GEOSPHERE)],
            name="incident_location_2dsphere",
            sparse=True,
        )
        logger.info("✓ Created geospatial index on safety_incidents")

        await safety_incidents.create_index(
            [("timestamp", DESCENDING), ("resolved", ASCENDING)],
            name="incident_time_resolved_idx",
        )
        logger.info("✓ Created compound index on safety_incidents (timestamp, resolved)")

        await safety_incidents.create_index(
            [("complaint_id", ASCENDING)],
            name="incident_complaint_idx",
        )
        logger.info("✓ Created index on safety_incidents.complaint_id")

        # ==================== OTP_VERIFICATIONS COLLECTION ====================
        otp_verifications = db["otp_verifications"]

        await otp_verifications.create_index(
            [("user_id", ASCENDING), ("phone", ASCENDING), ("purpose", ASCENDING)],
            name="otp_user_phone_purpose_idx",
        )
        logger.info("✓ Created compound index on otp_verifications")

        await otp_verifications.create_index(
            [("expires_at", ASCENDING)],
            name="otp_expiry_ttl",
            expireAfterSeconds=0,
        )
        logger.info("✓ Created TTL index on otp_verifications.expires_at")

        logger.info("✅ All MongoDB indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating MongoDB indexes: {e}")
        raise


async def seed_default_data(db: AsyncIOMotorDatabase) -> None:
    """Seed required demo users and officials if they do not already exist."""
    now = datetime.utcnow()

    demo_citizen = {
        "user_id": "CITI_DEMO_001",
        "name": "Demo Citizen",
        "email": "citizen_demo@example.com",
        "password_hash": pwd_context.hash("demo123"),
        "user_type": "citizen",
        "phone": "+91-9000000001",
        "ward_id": "ward_001",
        "verified": True,
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

    demo_official = {
        "user_id": "OFF_DEMO_001",
        "name": "Demo Official",
        "email": "official_demo@example.com",
        "password_hash": pwd_context.hash("demo123"),
        "user_type": "official",
        "phone": "+91-9000000002",
        "designation": "Public Works Supervisor",
        "department": "Public_Works",
        "ward_id": "ward_001",
        "authority_level": "supervisor",
        "office_address": "Municipal Office, Ward 001",
        "office_latitude": 22.5726,
        "office_longitude": 88.3639,
        "verified": True,
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
        "specializations": ["pothole", "road_damage", "drainage"],
        "team_members": [],
        "notification_preferences": {"email": True, "sms": False},
        "metadata": {},
        "created_at": now,
        "updated_at": now,
    }

    additional_officials = [
        {
            **demo_official,
            "user_id": "OFF_WS_001",
            "name": "Priya Sharma",
            "email": "priya.sharma@municipal.local",
            "department": "Water_Supply",
            "designation": "Water Supply Manager",
            "specializations": ["water_leak"],
        },
        {
            **demo_official,
            "user_id": "OFF_SAN_001",
            "name": "Vikram Singh",
            "email": "vikram.singh@municipal.local",
            "department": "Sanitation",
            "designation": "Sanitation Officer",
            "specializations": ["garbage"],
        },
        {
            **demo_official,
            "user_id": "OFF_COMM_001",
            "name": "Municipal Commissioner",
            "email": "commissioner@municipal.local",
            "department": "General_Services",
            "ward_id": "all",
            "authority_level": "commissioner",
            "designation": "Commissioner",
            "specializations": ["escalation"],
        },
    ]

    await db["citizens"].update_one(
        {"email": demo_citizen["email"]},
        {"$setOnInsert": demo_citizen},
        upsert=True,
    )
    await db["officials"].update_one(
        {"email": demo_official["email"]},
        {"$setOnInsert": demo_official},
        upsert=True,
    )

    for official in additional_officials:
        await db["officials"].update_one(
            {"email": official["email"]},
            {"$setOnInsert": official},
            upsert=True,
        )

    logger.info("✓ Seeded default users and officials")


async def drop_all_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Drop all indexes from collections (useful for development/testing).
    
    WARNING: Use this only in development. Production should not call this.
    
    Args:
        db: AsyncDatabase instance from motor
    """
    try:
        collections = [
            "complaints",
            "officials",
            "citizens",
            "wards",
            "escalations",
            "routes",
            "safety_heatmaps",
            "safety_incidents",
            "otp_verifications",
        ]

        for collection_name in collections:
            collection = db[collection_name]
            await collection.drop_indexes()
            logger.info(f"Dropped all indexes from {collection_name}")

        logger.info("✅ All indexes dropped successfully")

    except Exception as e:
        logger.error(f"❌ Error dropping indexes: {e}")
        raise


async def get_index_info(db: AsyncIOMotorDatabase, collection_name: str) -> dict:
    """
    Get information about indexes on a collection.
    
    Args:
        db: AsyncDatabase instance
        collection_name: Name of the collection
        
    Returns:
        Dictionary with index information
    """
    try:
        collection = db[collection_name]
        index_info = await collection.index_information()
        return index_info
    except Exception as e:
        logger.error(f"Error getting index info for {collection_name}: {e}")
        raise
