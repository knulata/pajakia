"""Basic smoke tests for PajakAI."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "PajakAI"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_webhook_verify(client):
    resp = await client.get(
        "/api/v1/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "pajakai-webhook-verify",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == 12345


@pytest.mark.asyncio
async def test_webhook_verify_bad_token(client):
    resp = await client.get(
        "/api/v1/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "wrong-token",
        },
    )
    assert resp.status_code == 403
