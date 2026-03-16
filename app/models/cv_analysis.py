from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Skor sonuçları
    ats_score: Mapped[float] = mapped_column(Float, nullable=True)
    format_score: Mapped[float] = mapped_column(Float, nullable=True)
    keyword_score: Mapped[float] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float] = mapped_column(Float, nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Detaylar
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    extracted_keywords: Mapped[dict] = mapped_column(JSON, nullable=True)
    suggestions: Mapped[dict] = mapped_column(JSON, nullable=True)

    # İlan eşleştirme
    job_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    job_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    job_match_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="analyses")
