import httpx
from openai import AsyncOpenAI

from app.config import get_settings
from app.models.cv_analysis import CVAnalysis
from app.core.exceptions import JobPostingFetchError, APIError

settings = get_settings()

# OpenAI client (lazy initialized)
_client = None


def get_openai_client() -> AsyncOpenAI:
    """OpenAI client döndür (lazy initialization)."""
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise APIError("OpenAI API key is not configured.")
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client

MATCH_PROMPT = """
CV anahtar kelimeleri: {cv_keywords}

İlan metni: {job_text}

Bu CV ile iş ilanının uyumunu analiz et. JSON formatında yanıt ver:
{{
    "match_score": 0-100 arası uyum skoru,
    "matching_keywords": ["eşleşen anahtar kelimeler"],
    "missing_keywords": ["CV'de eksik olup ilanda geçen anahtar kelimeler"],
    "suggestions": ["CV'yi bu ilana uygun hale getirmek için öneriler"]
}}
"""


async def match_cv_to_job(analysis: CVAnalysis, job_url: str) -> dict:
    """CV analiz sonucunu iş ilanıyla eşleştirir."""
    # İlan metnini çek
    job_text = await _fetch_job_posting(job_url)

    cv_keywords = analysis.extracted_keywords or {}

    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen bir CV-ilan eşleştirme uzmanısın. JSON formatında yanıt ver."},
                {"role": "user", "content": MATCH_PROMPT.format(cv_keywords=cv_keywords, job_text=job_text[:4000])},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        if isinstance(e, APIError) or "API key" in str(e) or "not configured" in str(e):
            return {
                "match_score": 0,
                "matching_keywords": [],
                "missing_keywords": [],
                "suggestions": ["OpenAI API key is not configured."],
            }
        return {
            "match_score": 0,
            "matching_keywords": [],
            "missing_keywords": [],
            "suggestions": ["Eşleştirme yapılamadı. Lütfen tekrar deneyin."],
        }


async def _fetch_job_posting(url: str) -> str:
    """İlan URL'sinden ilan metnini çeker."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as http_client:
            response = await http_client.get(url)
            response.raise_for_status()
            # Basit HTML → metin dönüştürme
            from app.utils.text_cleaner import strip_html_tags
            return strip_html_tags(response.text)
    except Exception:
        raise JobPostingFetchError("İlan sayfası yüklenemedi. URL'yi kontrol edin.")
