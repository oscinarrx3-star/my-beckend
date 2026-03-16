import re
import json
from openai import AsyncOpenAI
from app.config import get_settings
from app.core.exceptions import APIError

settings = get_settings()

# OpenAI client (lazy initialized)
_client = None


def get_openai_client():
    """OpenAI client döndür (lazy initialization)."""
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise APIError("OPENAI_API_KEY environment variable not set")
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


ANALYSIS_PROMPT = """
Sen bir CV analiz uzmanısın. Aşağıdaki CV metnini analiz et ve JSON formatında yanıt ver.

Analiz kriterleri:
1. **keywords**: CV'deki teknik ve yumuşak becerileri listele
2. **sections_found**: Bulunan bölümler (eğitim, deneyim, beceriler, projeler, vb.)
3. **missing_sections**: Eksik olan önemli bölümler
4. **format_issues**: Format sorunları (tarih tutarsızlıkları, eksik bilgiler)
5. **experience_years**: Toplam deneyim yılı (tahmini)
6. **language**: CV'nin dili
7. **contact_info**: İletişim bilgileri var mı (email, telefon, linkedin)
8. **action_verbs_used**: Kullanılan aksiyon fiilleri
9. **quantifiable_achievements**: Sayısal başarılar var mı

Yanıtı sadece JSON olarak ver, başka açıklama ekleme.

CV Metni:
{cv_text}
"""


async def analyze_cv_text(cv_text: str) -> dict:
    """CV metnini OpenAI API ile analiz eder veya fallback kullanır."""
    # Metni makul bir uzunlukta tut
    truncated = cv_text[:8000]

    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen bir profesyonel CV analiz uzmanısın. Yanıtlarını JSON formatında ver."},
                {"role": "user", "content": ANALYSIS_PROMPT.format(cv_text=truncated)},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"OpenAI API error: {e}. Fallback analiz kullanılıyor.")
        # Fallback: basit regex tabanlı analiz
        return _fallback_analysis(cv_text)


def _fallback_analysis(cv_text: str) -> dict:
    """OpenAI kullanılamazsa basit regex tabanlı analiz."""
    text_lower = cv_text.lower()

    sections = []
    section_keywords = {
        "eğitim": ["eğitim", "education", "üniversite", "university"],
        "deneyim": ["deneyim", "experience", "iş tecrübesi", "work"],
        "beceriler": ["beceri", "skills", "yetkinlik", "competencies"],
        "projeler": ["proje", "projects"],
        "sertifikalar": ["sertifika", "certificate", "certification"],
    }
    for section, keywords in section_keywords.items():
        if any(kw in text_lower for kw in keywords):
            sections.append(section)

    # E-posta ve telefon kontrolü
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', cv_text))
    has_phone = bool(re.search(r'[\+]?[0-9\s\-\(\)]{10,}', cv_text))

    # Aksiyon fiilleri
    action_verbs = ["geliştir", "yönet", "tasarla", "lider", "implement", "developed", "managed", "designed", "led"]
    verbs_found = [v for v in action_verbs if v in text_lower]

    return {
        "keywords": {"extracted": [], "note": "OpenAI API gerekli (detaylı analiz için)"},
        "sections_found": sections,
        "missing_sections": [s for s in section_keywords if s not in sections],
        "format_issues": [],
        "experience_years": 0,
        "language": "tr",
        "contact_info": {"email": has_email, "phone": has_phone, "linkedin": "linkedin" in text_lower},
        "action_verbs_used": verbs_found,
        "quantifiable_achievements": [],
    }
