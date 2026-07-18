"""Shared pytest configuration for current backend tests."""

import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("NVIDIA_API_KEY", "mock-nvidia-key")
os.environ.setdefault("SECRET_KEY", "test-secret")


@pytest.fixture
def sample_location_data():
    return {
        "latitude": 22.5726,
        "longitude": 88.3639,
        "address": "Test Street",
        "ward_id": "ward_001",
        "pin_code": "700001",
    }
