"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_uri: Optional[str] = None
    mongodb_database: str = "nagarseva_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # FastAPI
    api_title: str = "NagarSeva Backend"
    api_version: str = "0.1.0"
    api_description: str = "Multi-Agent Backend for Civic Issue Management"
    debug: bool = True
    environment: str = "development"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # NVIDIA NIM
    nvidia_api_key: str = "mock-nvidia-key"
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model_vision: str = "meta/llama-3.2-11b-vision-instruct"
    nvidia_model_text: str = "meta/llama-3.1-70b-instruct"
    nvidia_model_asr: Optional[str] = None

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10

    # Geospatial
    default_clustering_radius_meters: int = 500
    route_buffer_radius_meters: int = 300

    # Notifications
    enable_email_notifications: bool = False
    enable_sms_notifications: bool = False
    enable_push_notifications: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sms_api_key: Optional[str] = None
    sms_api_url: Optional[str] = None
    sms_sender_id: Optional[str] = None
    push_api_key: Optional[str] = None
    push_api_url: Optional[str] = None

    # Escalation
    escalation_check_interval_hours: int = 1
    overdue_complaint_days: int = 7
    escalation_levels: str = "ward_supervisor,department_head,commissioner"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
    cors_origin_regex: str = r"https://([a-z0-9]+--)?nagar-seva\.netlify\.app"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create global settings instance
settings = Settings()
if settings.mongodb_uri:
    settings.mongodb_url = settings.mongodb_uri
