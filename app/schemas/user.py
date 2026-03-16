from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_premium: bool
    free_analyses_used: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUsageResponse(BaseModel):
    free_analyses_used: int
    max_free_analyses: int
    is_premium: bool
    remaining_free: int
