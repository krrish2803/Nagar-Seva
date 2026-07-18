"""Tests for database-backed authentication helpers."""

from datetime import timedelta

import pytest

from app.utils import auth


class FakeUpdateResult:
    matched_count = 1


class FakeCollection:
    def __init__(self, document=None):
        self.document = document
        self.inserted = None

    async def find_one(self, query):
        if self.document and query.get("email") == self.document["email"]:
            return self.document
        return None

    async def update_one(self, *args, **kwargs):
        return FakeUpdateResult()

    async def insert_one(self, document):
        self.inserted = document

        class Result:
            inserted_id = "inserted-id"

        return Result()


class FakeDB:
    def __init__(self, citizen=None, official=None):
        self.collections = {
            "citizens": FakeCollection(citizen),
            "officials": FakeCollection(official),
        }

    def __getitem__(self, name):
        return self.collections[name]


def test_create_and_verify_access_token():
    token = auth.create_access_token("USER_1", "citizen", "user@example.com")
    payload = auth.verify_token(token)

    assert payload.sub == "USER_1"
    assert payload.user_type == "citizen"
    assert payload.email == "user@example.com"


def test_expired_token_is_rejected():
    token = auth.create_access_token(
        "USER_1",
        "citizen",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(Exception):
        auth.verify_token(token)


def test_password_hash_roundtrip():
    password_hash = auth.hash_password("demo123")

    assert password_hash != "demo123"
    assert auth.verify_password("demo123", password_hash)
    assert not auth.verify_password("wrong", password_hash)


@pytest.mark.asyncio
async def test_authenticate_user_reads_database(monkeypatch):
    citizen = {
        "_id": "db-id",
        "user_id": "CITI_1",
        "email": "citizen@example.com",
        "password_hash": auth.hash_password("demo123"),
        "user_type": "citizen",
        "account_status": "active",
    }
    fake_db = FakeDB(citizen=citizen)
    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(auth, "get_database", fake_get_database)

    user = await auth.authenticate_user("citizen@example.com", "demo123")

    assert user["user_id"] == "CITI_1"
    assert user["user_type"] == "citizen"


@pytest.mark.asyncio
async def test_authenticate_user_rejects_bad_password(monkeypatch):
    citizen = {
        "_id": "db-id",
        "user_id": "CITI_1",
        "email": "citizen@example.com",
        "password_hash": auth.hash_password("demo123"),
        "user_type": "citizen",
        "account_status": "active",
    }
    async def fake_get_database():
        return FakeDB(citizen=citizen)

    monkeypatch.setattr(auth, "get_database", fake_get_database)

    assert await auth.authenticate_user("citizen@example.com", "bad") is None
