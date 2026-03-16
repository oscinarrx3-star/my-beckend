from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.api.v1.router import api_router
from app.core.middleware import setup_middleware
from app.logging_config import setup_logging


# Logging setup
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Application shutting down...")


settings = get_settings()

app = FastAPI(
    title="CV Analiz & ATS Skoru API",
    description="AI destekli CV analiz ve ATS uyumluluk skorlama servisi",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_middleware(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check called")
    return {"status": "ok"}
