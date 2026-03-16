import pytest


@pytest.mark.asyncio
async def test_create_payment_requires_auth(client):
    response = await client.post("/api/v1/payment/create", json={
        "payment_type": "per_analysis",
        "provider": "iyzico",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_payment_iyzico(client, registered_user_token):
    """iyzico ödeme oluştur."""
    response = await client.post(
        "/api/v1/payment/create",
        json={
            "payment_type": "per_analysis",
            "provider": "iyzico",
        },
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "payment_id" in data
    assert "checkout_url" in data
    assert data["amount"] == 9.0
    assert data["currency"] == "TRY"


@pytest.mark.asyncio
async def test_create_payment_stripe(client, registered_user_token):
    """Stripe ödeme oluştur."""
    response = await client.post(
        "/api/v1/payment/create",
        json={
            "payment_type": "subscription",
            "provider": "stripe",
        },
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "payment_id" in data
    assert data["amount"] == 29.0


@pytest.mark.asyncio
async def test_payment_callback_iyzico(client):
    """iyzico callback işlemeyi test et."""
    response = await client.post(
        "/api/v1/payment/callback/iyzico",
        json={
            "paymentId": "1",
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"


@pytest.mark.asyncio
async def test_payment_callback_stripe(client):
    """Stripe webhook işlemeyi test et."""
    response = await client.post(
        "/api/v1/payment/callback/stripe",
        json={
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                }
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
