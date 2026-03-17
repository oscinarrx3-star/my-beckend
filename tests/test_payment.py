import pytest
from unittest.mock import patch


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
    assert registered_user_token != ""
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
    assert registered_user_token != ""
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


@pytest.mark.asyncio
async def test_payment_callback_iyzico_updates_payment(client, registered_user_token, db_session):
    """iyzico SUCCESS callback ödemeyi tamamlandı olarak işaretlemeli ve transaction_id set etmeli."""
    assert registered_user_token != ""
    # Önce bir ödeme oluştur
    create_resp = await client.post(
        "/api/v1/payment/create",
        json={"payment_type": "per_analysis", "provider": "iyzico"},
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert create_resp.status_code == 200
    payment_id = create_resp.json()["payment_id"]

    # Callback gönder
    callback_resp = await client.post(
        "/api/v1/payment/callback/iyzico",
        json={
            "paymentId": str(payment_id),
            "status": "SUCCESS",
            "referenceCode": "ref_abc123",
        },
    )
    assert callback_resp.status_code == 200

    # DB'deki ödemeyi doğrula
    from sqlalchemy import select
    from app.models.payment import Payment
    result = await db_session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    assert payment is not None
    assert payment.status == "completed"
    assert payment.transaction_id == "ref_abc123"


@pytest.mark.asyncio
async def test_payment_callback_stripe_invalid_signature(client):
    """Geçersiz Stripe imzası ile callback 400 döndürmeli."""
    with patch("app.services.payment_service.settings") as mock_settings:
        mock_settings.STRIPE_WEBHOOK_SECRET = "whsec_testsecret"
        mock_settings.STRIPE_SECRET_KEY = ""

        response = await client.post(
            "/api/v1/payment/callback/stripe",
            content=b'{"type":"payment_intent.succeeded","data":{"object":{"id":"pi_test"}}}',
            headers={
                "content-type": "application/json",
                "stripe-signature": "t=1234,v1=invalidsignature",
            },
        )
    assert response.status_code == 400
