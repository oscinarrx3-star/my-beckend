from fastapi import APIRouter

from app.api.v1.endpoints import auth, cv, job, payment, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cv.router, prefix="/cv", tags=["CV Analysis"])
api_router.include_router(job.router, prefix="/job", tags=["Job Matching"])
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
