from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas.user import UserResponse, UserUsageResponse
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()
settings = get_settings()


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return user


@router.get("/usage", response_model=UserUsageResponse)
async def get_usage(user: User = Depends(get_current_user)):
    remaining = max(0, settings.MAX_FREE_ANALYSES - user.free_analyses_used)
    return UserUsageResponse(
        free_analyses_used=user.free_analyses_used,
        max_free_analyses=settings.MAX_FREE_ANALYSES,
        is_premium=user.is_premium,
        remaining_free=remaining if not user.is_premium else -1,
    )
