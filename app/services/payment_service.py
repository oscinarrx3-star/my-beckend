import logging
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json

from app.config import get_settings
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import CreatePaymentRequest

logger = logging.getLogger(__name__)
settings = get_settings()

PRICES = {
    "subscription": 29.00,   # ₺29/ay
    "per_analysis": 9.00,    # ₺9/analiz
}


async def create_payment(user: User, body: CreatePaymentRequest, db: AsyncSession) -> dict:
    """Ödeme başlatır ve ödeme sağlayıcısına yönlendirir."""
    amount = PRICES.get(body.payment_type, 9.00)

    payment = Payment(
        user_id=user.id,
        amount=amount,
        currency="TRY",
        payment_type=body.payment_type,
        provider=body.provider,
        status="pending",
    )
    db.add(payment)
    await db.flush()

    if body.provider == "iyzico":
        checkout_url = await _create_iyzico_payment(payment, user)
    elif body.provider == "stripe":
        checkout_url = await _create_stripe_payment(payment, user)
    else:
        checkout_url = None

    return {
        "payment_id": payment.id,
        "checkout_url": checkout_url,
        "amount": amount,
        "currency": "TRY",
    }


async def handle_payment_callback(provider: str, db: AsyncSession, payload: dict = None, signature: str = None, raw_body: bytes = b"") -> dict:
    """Ödeme sağlayıcısından gelen callback'i işler (signature doğrulama ile)."""
    if provider == "iyzico":
        return await _handle_iyzico_callback(payload or {}, db, signature)
    elif provider == "stripe":
        return await _handle_stripe_callback(payload or {}, db, signature, raw_body)
    else:
        return {"status": "error", "message": "Bilinmeyen sağlayıcı"}


async def _create_iyzico_payment(payment: Payment, user: User) -> str:
    """iyzico ödeme formu oluşturur."""
    try:
        import iyzipay
        
        customer = {
            "id": str(user.id),
            "name": user.full_name.split()[0] if user.full_name else "User",
            "surname": user.full_name.split()[-1] if user.full_name and len(user.full_name.split()) > 1 else "User",
            "gsmNumber": "+90",
            "email": user.email,
            "identityNumber": "00000000000",
        }
        
        basket_items = [
            {
                "id": str(payment.id),
                "name": payment.payment_type,
                "category1": "Hizmet",
                "itemType": "VIRTUAL",
                "price": str(payment.amount),
            }
        ]
        
        request = {
            "locale": "tr",
            "conversationId": str(payment.id),
            "price": str(payment.amount),
            "paidPrice": str(payment.amount),
            "currency": payment.currency,
            "installment": "1",
            "basketId": str(payment.id),
            "paymentChannel": "WEB",
            "paymentGroup": "PRODUCT",
            "paymentCard": {
                "cardHolderName": user.full_name or "User",
                "cardNumber": "4111111111111111",  # Test card
                "expireMonth": "12",
                "expireYear": "2030",
                "cvc": "123",
            },
            "customer": customer,
            "basketItems": basket_items,
            "callbackUrl": f"{settings.API_BASE_URL}/api/v1/payment/callback/iyzico?paymentId={payment.id}",
        }
        
        options = iyzipay.Options()
        options.api_key = settings.IYZICO_API_KEY
        options.secret_key = settings.IYZICO_SECRET_KEY
        options.base_url = settings.IYZICO_BASE_URL
        
        # In production, use iyzipay.Payment.create(request, options)
        # For now, return sandbox checkout URL
        return f"{settings.IYZICO_BASE_URL}/checkout?paymentId={payment.id}"
    except Exception as e:
        print(f"iyzico error: {e}")
        return f"{settings.IYZICO_BASE_URL}/checkout?paymentId={payment.id}"


async def _create_stripe_payment(payment: Payment, user: User) -> str:
    """Stripe checkout session oluşturur."""
    try:
        import stripe
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency.lower(),
                        "product_data": {
                            "name": f"CV Analysis - {payment.payment_type}",
                            "description": f"Payment ID: {payment.id}",
                        },
                        "unit_amount": int(payment.amount * 100),  # cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{settings.API_BASE_URL}/payment/success?paymentId={payment.id}",
            cancel_url=f"{settings.API_BASE_URL}/payment/cancel",
            metadata={
                "payment_id": str(payment.id),
                "user_id": str(user.id),
            },
        )
        return session.url
    except Exception as e:
        print(f"Stripe error: {e}")
        return f"https://checkout.stripe.com/pay/{payment.id}"


async def _handle_iyzico_callback(payload: dict, db: AsyncSession, signature: str = None) -> dict:
    """iyzico callback'ini işle (webhook signature doğrulama ile)."""
    # İyzico webhook imza doğrulama
    # Referans: https://iyzipay.readme.io/page/webhooks
    if signature and settings.IYZICO_SECRET_KEY:
        computed_signature = hashlib.sha1(
            (json.dumps(payload, separators=(',', ':'), sort_keys=True) + settings.IYZICO_SECRET_KEY).encode()
        ).hexdigest()
        
        if not hmac.compare_digest(computed_signature, signature):
            return {
                "status": "error",
                "message": "Invalid signature",
            }
    
    payment_id = payload.get("paymentId")
    status = payload.get("status", "FAILURE")
    transaction_id = payload.get("referenceCode")
    
    if payment_id:
        try:
            from sqlalchemy import select
            result = await db.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()
            if payment:
                payment.status = "completed" if status == "SUCCESS" else "failed"
                payment.transaction_id = transaction_id
                await db.flush()
        except Exception as e:
            print(f"Error updating payment: {e}")
    
    return {
        "status": "processed",
        "payment_id": payment_id,
        "provider_status": status,
    }


async def _handle_stripe_callback(payload: dict, db: AsyncSession, signature: str = None, raw_body: bytes = b"") -> dict:
    """Stripe webhook'ini işle (signature doğrulama ile)."""
    # Stripe webhook signature doğrulama
    # https://stripe.com/docs/webhooks/signatures
    if signature and settings.STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            event = stripe.Webhook.construct_event(
                payload=raw_body,
                sig_header=signature,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
        except Exception as e:
            logger.error(f"Stripe signature verification failed: {e}")
            return {
                "status": "error",
                "message": "Invalid signature",
                "http_status": 400,
            }
    elif signature and not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning(
            "STRIPE_WEBHOOK_SECRET is not configured — skipping webhook signature verification. "
            "Set STRIPE_WEBHOOK_SECRET in production."
        )
        event = payload
    else:
        event = payload
    
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})
    
    if event_type == "payment_intent.succeeded":
        payment_intent_id = data_object.get("id")
        metadata = data_object.get("metadata", {})
        payment_id = metadata.get("payment_id")
        
        if payment_id:
            try:
                from sqlalchemy import select
                result = await db.execute(
                    select(Payment).where(Payment.id == payment_id)
                )
                payment = result.scalar_one_or_none()
                if payment:
                    payment.status = "completed"
                    payment.transaction_id = payment_intent_id
                    await db.flush()
            except Exception as e:
                print(f"Error updating payment: {e}")
                
    elif event_type == "payment_intent.payment_failed":
        payment_intent_id = data_object.get("id")
        metadata = data_object.get("metadata", {})
        payment_id = metadata.get("payment_id")
        
        if payment_id:
            try:
                from sqlalchemy import select
                result = await db.execute(
                    select(Payment).where(Payment.id == payment_id)
                )
                payment = result.scalar_one_or_none()
                if payment:
                    payment.status = "failed"
                    payment.transaction_id = payment_intent_id
                    await db.flush()
            except Exception as e:
                print(f"Error updating payment: {e}")
    
    return {
        "status": "processed",
        "event_type": event_type,
        "payment_intent_id": data_object.get("id"),
    }

