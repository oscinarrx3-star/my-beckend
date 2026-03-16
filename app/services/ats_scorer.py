def calculate_ats_score(nlp_result: dict) -> dict:
    """NLP analiz sonucuna göre ATS skorunu hesaplar."""

    # Format skoru (0-100)
    format_score = _calculate_format_score(nlp_result)

    # Anahtar kelime skoru (0-100)
    keyword_score = _calculate_keyword_score(nlp_result)

    # Deneyim skoru (0-100)
    experience_score = _calculate_experience_score(nlp_result)

    # ATS uyumluluk skoru (0-100)
    ats_score = _calculate_ats_compatibility(nlp_result)

    # Genel skor (ağırlıklı ortalama)
    overall_score = (
        format_score * 0.20
        + keyword_score * 0.30
        + experience_score * 0.20
        + ats_score * 0.30
    )

    return {
        "format_score": round(format_score, 1),
        "keyword_score": round(keyword_score, 1),
        "experience_score": round(experience_score, 1),
        "ats_score": round(ats_score, 1),
        "overall_score": round(overall_score, 1),
    }


def _calculate_format_score(nlp_result: dict) -> float:
    score = 50.0
    sections = nlp_result.get("sections_found", [])
    missing = nlp_result.get("missing_sections", [])

    # Her bulunan bölüm için puan
    score += len(sections) * 10
    # Her eksik bölüm için ceza
    score -= len(missing) * 5

    # İletişim bilgileri
    contact = nlp_result.get("contact_info", {})
    if contact.get("email"):
        score += 10
    if contact.get("phone"):
        score += 5
    if contact.get("linkedin"):
        score += 5

    # Format sorunları
    issues = nlp_result.get("format_issues", [])
    score -= len(issues) * 5

    return max(0, min(100, score))


def _calculate_keyword_score(nlp_result: dict) -> float:
    score = 30.0
    keywords = nlp_result.get("keywords", {})

    if isinstance(keywords, dict):
        keyword_list = keywords.get("extracted", [])
    elif isinstance(keywords, list):
        keyword_list = keywords
    else:
        keyword_list = []

    # Her anahtar kelime için puan
    score += len(keyword_list) * 3

    # Aksiyon fiilleri
    verbs = nlp_result.get("action_verbs_used", [])
    score += len(verbs) * 2

    # Sayısal başarılar
    achievements = nlp_result.get("quantifiable_achievements", [])
    score += len(achievements) * 5

    return max(0, min(100, score))


def _calculate_experience_score(nlp_result: dict) -> float:
    years = nlp_result.get("experience_years", 0)
    if isinstance(years, (int, float)):
        # 0 yıl = 20, 5+ yıl = 100
        return min(100, 20 + years * 16)
    return 30.0


def _calculate_ats_compatibility(nlp_result: dict) -> float:
    """ATS tarafından doğru parse edilebilirlik skoru."""
    score = 60.0

    sections = nlp_result.get("sections_found", [])
    if len(sections) >= 3:
        score += 15

    contact = nlp_result.get("contact_info", {})
    if contact.get("email") and contact.get("phone"):
        score += 10

    # Format sorunları ATS'yi olumsuz etkiler
    issues = nlp_result.get("format_issues", [])
    score -= len(issues) * 8

    return max(0, min(100, score))
