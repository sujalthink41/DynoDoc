"""E2E: the /health liveness probe through the full ASGI stack."""

from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "DynoDoc"
    assert body["environment"] == "test"


async def test_health_echoes_request_id_header(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.headers.get("X-Request-ID")


async def test_health_honours_inbound_request_id(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "fixed-id-123"})
    assert response.headers["X-Request-ID"] == "fixed-id-123"
