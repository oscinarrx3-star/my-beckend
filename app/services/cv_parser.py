import fitz  # PyMuPDF
import pdfplumber

from app.core.exceptions import PDFParseError


def parse_pdf(file_path: str) -> str:
    """PDF dosyasından metin çıkarır. Önce PyMuPDF, başarısız olursa pdfplumber dener."""
    text = _parse_with_pymupdf(file_path)
    if not text.strip():
        text = _parse_with_pdfplumber(file_path)
    return text


def _parse_with_pymupdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except Exception:
        return ""


def _parse_with_pdfplumber(file_path: str) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
    except Exception:
        raise PDFParseError("PDF dosyası okunamadı. Dosya bozuk olabilir.")
