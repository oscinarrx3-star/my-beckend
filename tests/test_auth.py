import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test1234!",
        "full_name": "Test Kullanıcı",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    payload = {
        "email": "test@example.com",
        "password": "Test1234!",
        "full_name": "Test Kullanıcı",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "Test1234!",
        "full_name": "Login User",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "Test1234!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "noone@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401
