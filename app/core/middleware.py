import time
import logging

from fastapi import FastAPI, Request

logger = logging.getLogger("cv_analiz")


def setup_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)"
        )
        return response
