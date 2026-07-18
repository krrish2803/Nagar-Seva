"""API routers package."""

from .complaints import router as complaints_router
from .heatmap import router as heatmap_router
from .routes import router as routes_router
from .escalation import router as escalation_router
from .auth import router as auth_router

__all__ = [
    "complaints_router",
    "heatmap_router",
    "routes_router",
    "escalation_router",
    "auth_router",
]
