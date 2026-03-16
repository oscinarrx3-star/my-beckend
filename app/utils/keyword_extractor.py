import re

# Türkçe ve İngilizce yaygın teknik beceriler
TECH_KEYWORDS = {
    "python", "javascript", "typescript", "java", "c#", "c++", "go", "rust", "ruby",
    "react", "angular", "vue", "svelte", "node.js", "django", "flask", "fastapi",
    "spring", ".net", "docker", "kubernetes", "aws", "azure", "gcp",
    "sql", "postgresql", "mysql", "mongodb", "redis",
    "git", "ci/cd", "rest", "graphql", "microservices",
    "machine learning", "deep learning", "nlp", "data science",
    "figma", "photoshop", "agile", "scrum", "jira",
}

SOFT_SKILLS_TR = {
    "liderlik", "iletişim", "takım çalışması", "problem çözme", "analitik düşünme",
    "zaman yönetimi", "proje yönetimi", "sunum", "müzakere", "adaptasyon",
}


def extract_keywords(text: str) -> dict:
    """Metinden teknik ve yumuşak becerileri çıkarır."""
    text_lower = text.lower()

    found_tech = [kw for kw in TECH_KEYWORDS if kw in text_lower]
    found_soft = [kw for kw in SOFT_SKILLS_TR if kw in text_lower]

    # Yıl bazlı deneyim kalıpları
    experience_patterns = re.findall(r'(\d+)\s*(?:yıl|year|sene)', text_lower)
    years = [int(y) for y in experience_patterns]

    return {
        "technical_skills": sorted(found_tech),
        "soft_skills": sorted(found_soft),
        "experience_years_mentioned": years,
    }
