from pydantic import BaseModel
from datetime import datetime


class CVAnalysisResponse(BaseModel):
    id: int
    file_name: str
    ats_score: float | None
    format_score: float | None
    keyword_score: float | None
    experience_score: float | None
    overall_score: float | None
    extracted_keywords: dict | None
    suggestions: dict | None
    job_url: str | None
    job_match_score: float | None
    job_match_details: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CVUploadResponse(BaseModel):
    message: str
    analysis_id: int


class CVScoreSummary(BaseModel):
    overall_score: float
    ats_score: float
    format_score: float
    keyword_score: float
    experience_score: float
    suggestions: list[str]
