import re


def strip_html_tags(html: str) -> str:
    """HTML etiketlerini temizleyip düz metin döndürür."""
    # Script ve style blokları
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # HTML etiketleri
    text = re.sub(r'<[^>]+>', ' ', text)
    # HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    # Fazla boşluklar
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_whitespace(text: str) -> str:
    """Fazla boşlukları ve satır sonlarını temizler."""
    return re.sub(r'\s+', ' ', text).strip()


def truncate_text(text: str, max_length: int = 5000) -> str:
    """Metni belirli uzunlukta keser."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
