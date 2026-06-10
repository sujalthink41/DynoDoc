"""E2E: the sign-in flow via the dev-login path (no real Google needed)."""

from httpx import AsyncClient


async def test_dev_login_then_me(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/dev-login", json={"email": "dev@example.com", "name": "Dev"}
    )
    assert login.status_code == 200
    assert login.json()["email"] == "dev@example.com"

    me = await client.get("/api/v1/me")
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "dev@example.com"
    assert body["display_name"] == "Dev"
    assert body["is_active"] is True


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"


async def test_logout_clears_the_session(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/dev-login", json={"email": "dev@example.com"})
    assert (await client.get("/api/v1/me")).status_code == 200

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert (await client.get("/api/v1/me")).status_code == 401


async def test_second_login_reuses_same_user(client: AsyncClient) -> None:
    first = await client.post("/api/v1/auth/dev-login", json={"email": "dev@example.com"})
    second = await client.post("/api/v1/auth/dev-login", json={"email": "dev@example.com"})
    assert first.json()["id"] == second.json()["id"]
