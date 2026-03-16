import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.config import get_settings
from app.schemas.cv import CVAnalysisResponse, CVUploadResponse
from app.models.cv_analysis import CVAnalysis
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.cv_parser import parse_pdf
from app.services.nlp_analyzer import analyze_cv_text
from app.services.ats_scorer import calculate_ats_score
from app.services.suggestion_engine import generate_suggestions
from app.core.exceptions import FreeLimitExceeded, PDFParseError

router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=CVUploadResponse, status_code=201)
async def upload_cv(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Limit kontrolü
    if not user.is_premium and user.free_analyses_used >= settings.MAX_FREE_ANALYSES:
        raise FreeLimitExceeded()

    # Dosya kaydet
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "cv.pdf")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # PDF parse
    extracted_text = parse_pdf(file_path)
    if not extracted_text.strip():
        raise PDFParseError("PDF'den metin çıkarılamadı. Lütfen metin tabanlı bir PDF yükleyin.")

    # NLP analiz
    nlp_result = await analyze_cv_text(extracted_text)

    # ATS skor
    scores = calculate_ats_score(nlp_result)

    # Öneriler
    suggestions = generate_suggestions(nlp_result, scores)

    # DB kayıt
    analysis = CVAnalysis(
        user_id=user.id,
        file_name=file.filename or "cv.pdf",
        file_path=file_path,
        extracted_text=extracted_text,
        extracted_keywords=nlp_result.get("keywords", {}),
        ats_score=scores["ats_score"],
        format_score=scores["format_score"],
        keyword_score=scores["keyword_score"],
        experience_score=scores["experience_score"],
        overall_score=scores["overall_score"],
        suggestions=suggestions,
    )
    db.add(analysis)

    # Kullanım sayacını artır
    user.free_analyses_used += 1
    await db.flush()

    return CVUploadResponse(message="CV başarıyla analiz edildi", analysis_id=analysis.id)


@router.get("/analyses", response_model=list[CVAnalysisResponse])
async def list_analyses(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CVAnalysis).where(CVAnalysis.user_id == user.id).order_by(CVAnalysis.created_at.desc())
    )
    return result.scalars().all()


@router.get("/analyses/{analysis_id}", response_model=CVAnalysisResponse)
async def get_analysis(
    analysis_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CVAnalysis).where(CVAnalysis.id == analysis_id, CVAnalysis.user_id == user.id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    return analysis
