import pytest


@pytest.mark.asyncio
async def test_match_requires_auth(client):
    response = await client.post("/api/v1/job/match", json={
        "analysis_id": 1,
        "job_url": "https://example.com/job/123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_match_analysis_not_found(client, registered_user_token):
    """Mevcut olmayan analiz için 404 dönmeli."""
    response = await client.post(
        "/api/v1/job/match",
        json={
            "analysis_id": 99999,
            "job_url": "https://example.com/job/123",
        },
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_match_requires_valid_token(client):
    """Geçersiz token ile maruz kalınan talepler reddedilmeli."""
    response = await client.post(
        "/api/v1/job/match",
        json={
            "analysis_id": 1,
            "job_url": "https://example.com/job/123",
        },
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code in [401, 422]
