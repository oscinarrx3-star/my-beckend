from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Database session döndür (error handling ile)."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Database tabloları oluştur."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
