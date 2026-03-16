from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import Settings, get_settings


def get_current_settings() -> Settings:
    return get_settings()


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db
