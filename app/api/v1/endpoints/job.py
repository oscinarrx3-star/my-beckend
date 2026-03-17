from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.job import JobMatchRequest, JobMatchResponse
from app.models.cv_analysis import CVAnalysis
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.job_matcher import match_cv_to_job

router = APIRouter()


@router.post("/match", response_model=JobMatchResponse)
async def match_job(
    body: JobMatchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CVAnalysis).where(CVAnalysis.id == body.analysis_id, CVAnalysis.user_id == user.id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")

    match_result = await match_cv_to_job(analysis, str(body.job_url))

    # Sonuçları güncelle
    analysis.job_url = str(body.job_url)
    analysis.job_match_score = match_result["match_score"]
    analysis.job_match_details = match_result
    await db.flush()

    return JobMatchResponse(**match_result)
