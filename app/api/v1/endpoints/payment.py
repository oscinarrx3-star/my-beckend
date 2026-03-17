from fastapi import APIRouter, Depends, Request, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.payment import CreatePaymentRequest
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.payment_service import create_payment, handle_payment_callback

router = APIRouter()


@router.post("/create", response_model=dict)
async def initiate_payment(
    body: CreatePaymentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await create_payment(user, body, db)
    await db.commit()
    return result


@router.post("/callback/{provider}")
async def payment_callback(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_iyzico_signature: str = Header(None),
    stripe_signature: str = Header(None),
):
    """iyzico/Stripe webhook callback"""
    raw_body = await request.body()
    try:
        import json
        payload = json.loads(raw_body) if raw_body else {}
    except Exception:
        payload = {}

    # Imza doğrulama
    signature = x_iyzico_signature if provider == "iyzico" else stripe_signature

    result = await handle_payment_callback(provider, db, payload, signature, raw_body)
    if result.get("status") == "error" and result.get("http_status") == 400:
        raise HTTPException(status_code=400, detail=result.get("message", "Bad request"))
    await db.commit()
    return result
