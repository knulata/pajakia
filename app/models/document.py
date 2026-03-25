import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    BUKTI_POTONG_A1 = "bukti_potong_1721_a1"
    BUKTI_POTONG_A2 = "bukti_potong_1721_a2"
    FAKTUR_PAJAK = "faktur_pajak"
    BUKTI_POTONG_PPH23 = "bukti_potong_pph23"
    BUKTI_POTONG_PPH26 = "bukti_potong_pph26"
    BUKTI_POTONG_PPH4_2 = "bukti_potong_pph4_2"
    INVOICE = "invoice"
    FINANCIAL_STATEMENT = "financial_statement"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    filing_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tax_filings.id"), index=True
    )
    doc_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType), default=DocumentType.OTHER
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED
    )
    file_url: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int | None] = mapped_column()

    # OCR results
    extracted_data: Mapped[dict | None] = mapped_column(JSON)
    ocr_confidence: Mapped[float | None] = mapped_column()
    ocr_raw_text: Mapped[str | None] = mapped_column(Text)

    # Tax period this document belongs to
    tax_year: Mapped[int | None] = mapped_column()
    tax_month: Mapped[int | None] = mapped_column()  # For SPT Masa

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="documents")
    filing: Mapped["TaxFiling | None"] = relationship(back_populates="documents")
