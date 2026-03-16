from pydantic import BaseModel, HttpUrl


class JobMatchRequest(BaseModel):
    analysis_id: int
    job_url: HttpUrl


class JobMatchResponse(BaseModel):
    match_score: float
    matching_keywords: list[str]
    missing_keywords: list[str]
    suggestions: list[str]
