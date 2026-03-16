from pydantic import BaseModel
from datetime import datetime


class CreatePaymentRequest(BaseModel):
    payment_type: str  # "subscription" | "per_analysis"
    provider: str  # "iyzico" | "stripe"


class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    payment_type: str
    provider: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCallbackRequest(BaseModel):
    provider_payment_id: str
    status: str
