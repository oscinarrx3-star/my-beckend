import pytest
from unittest.mock import patch, AsyncMock


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


@pytest.mark.asyncio
async def test_match_job_missing_openai_key(client, registered_user_token, db_session):
    """OPENAI_API_KEY yokken job match anlamlı hata / fallback döndürmeli."""
    import app.services.job_matcher as jm

    # Create a CV analysis in db so the endpoint finds it
    from app.models.cv_analysis import CVAnalysis
    from app.models.user import User
    from sqlalchemy import select

    user_result = await db_session.execute(select(User).where(User.email == "fixture@example.com"))
    user = user_result.scalar_one_or_none()
    assert user is not None

    analysis = CVAnalysis(
        user_id=user.id,
        file_name="test.pdf",
        file_path="/tmp/test.pdf",
        extracted_text="Python developer with 3 years experience",
        extracted_keywords={"python": 5},
        ats_score=70.0,
        format_score=70.0,
        keyword_score=70.0,
        experience_score=70.0,
        overall_score=70.0,
        suggestions=[],
    )
    db_session.add(analysis)
    await db_session.flush()
    analysis_id = analysis.id

    # Reset the cached client so it re-evaluates with empty key
    original_client = jm._client
    jm._client = None

    with patch.object(jm.settings, "OPENAI_API_KEY", ""):
        # Mock _fetch_job_posting to avoid network call
        with patch.object(jm, "_fetch_job_posting", new=AsyncMock(return_value="Python job posting")):
            response = await client.post(
                "/api/v1/job/match",
                json={"analysis_id": analysis_id, "job_url": "https://example.com/job/1"},
                headers={"Authorization": f"Bearer {registered_user_token}"},
            )

    # Restore client state
    jm._client = original_client

    # Acceptable: 200 with fallback data, 422, or 503
    assert response.status_code in [200, 422, 503]
    if response.status_code == 200:
        data = response.json()
        # Should contain a meaningful error message in suggestions
        suggestions = data.get("suggestions", [])
        assert any("OpenAI" in s or "key" in s.lower() or "configured" in s.lower() for s in suggestions)
    elif response.status_code in [422, 503]:
        data = response.json()
        assert "detail" in data
