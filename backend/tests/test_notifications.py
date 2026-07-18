"""Tests for notification provider integrations."""

import pytest

from app.utils import notifications


class FakeResponse:
    def raise_for_status(self):
        return None


class FakeAsyncClient:
    requests = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, headers=None, json=None):
        self.requests.append({"url": url, "headers": headers, "json": json})
        return FakeResponse()


@pytest.mark.asyncio
async def test_send_sms_calls_configured_provider(monkeypatch):
    FakeAsyncClient.requests = []
    monkeypatch.setattr(notifications.httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(notifications.settings, "enable_sms_notifications", True)
    monkeypatch.setattr(notifications.settings, "sms_api_url", "https://sms.example.test/send")
    monkeypatch.setattr(notifications.settings, "sms_api_key", "test-key")
    monkeypatch.setattr(notifications.settings, "sms_sender_id", "NagarSeva")

    assert await notifications.send_sms("+910000000000", "Hello")
    assert FakeAsyncClient.requests[0]["json"]["to"] == "+910000000000"
    assert FakeAsyncClient.requests[0]["json"]["message"] == "Hello"


@pytest.mark.asyncio
async def test_send_push_calls_configured_provider(monkeypatch):
    FakeAsyncClient.requests = []
    monkeypatch.setattr(notifications.httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(notifications.settings, "enable_push_notifications", True)
    monkeypatch.setattr(notifications.settings, "push_api_url", "https://push.example.test/send")
    monkeypatch.setattr(notifications.settings, "push_api_key", "test-key")

    assert await notifications.send_push_notification("USER_1", "Title", "Body", {"x": 1})
    assert FakeAsyncClient.requests[0]["json"]["user_id"] == "USER_1"
    assert FakeAsyncClient.requests[0]["json"]["data"] == {"x": 1}
