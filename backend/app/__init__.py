"""NagarSeva FastAPI Backend package."""

__version__ = "0.1.0"
__author__ = "NagarSeva Team"
__description__ = "Multi-Agent Backend for Civic Issue Management"

from app.config import settings
from app.main import app

__all__ = ["app", "settings", "__version__"]
