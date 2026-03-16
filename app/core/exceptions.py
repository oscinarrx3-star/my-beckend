from fastapi import HTTPException, status


class APIError(HTTPException):
    """Genel API hatası (OpenAI, payment vb.)."""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class CVAnalysisException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class PDFParseError(CVAnalysisException):
    def __init__(self, detail: str = "PDF dosyası okunamadı"):
        super().__init__(detail=detail)


class FreeLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Ücretsiz analiz hakkınız doldu. Devam etmek için abonelik alın.",
        )


class JobPostingFetchError(CVAnalysisException):
    def __init__(self, detail: str = "İlan bilgileri alınamadı"):
        super().__init__(detail=detail)


class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kayıtlı",
        )


class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
        )
