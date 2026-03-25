import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class FilingType(str, enum.Enum):
    # Individual
    SPT_1770SS = "spt_1770ss"  # Simple employee, single employer, <60M/yr
    SPT_1770S = "spt_1770s"  # Employee with multiple income sources
    SPT_1770 = "spt_1770"  # Freelancer / business owner

    # Corporate
    SPT_1771 = "spt_1771"  # PPh Badan (corporate income tax)

    # Monthly (SPT Masa)
    SPT_MASA_PPN = "spt_masa_ppn"  # Monthly VAT
    SPT_MASA_PPH21 = "spt_masa_pph21"  # Monthly employee withholding
    SPT_MASA_PPH23 = "spt_masa_pph23"  # Monthly service withholding
    SPT_MASA_PPH25 = "spt_masa_pph25"  # Monthly installment
    SPT_MASA_PPH4_2 = "spt_masa_pph4_2"  # Final tax (rent, construction, etc.)


class FilingStatus(str, enum.Enum):
    DRAFT = "draft"
    DATA_COLLECTION = "data_collection"
    AI_PROCESSING = "ai_processing"
    REVIEW = "review"  # Ready for human review
    APPROVED = "approved"  # Reviewed by consultant or taxpayer
    FILED = "filed"  # Submitted to DJP/Coretax
    ACCEPTED = "accepted"  # Acknowledged by DJP
    REJECTED = "rejected"  # Rejected by DJP
    AMENDED = "amended"  # Pembetulan filed


class TaxFiling(Base):
    __tablename__ = "tax_filings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    consultant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    filing_type: Mapped[FilingType] = mapped_column(SQLEnum(FilingType))
    status: Mapped[FilingStatus] = mapped_column(
        SQLEnum(FilingStatus), default=FilingStatus.DRAFT
    )

    # Tax period
    tax_year: Mapped[int] = mapped_column()
    tax_month: Mapped[int | None] = mapped_column()  # Null for annual, 1-12 for masa

    # Computed tax data
    gross_income: Mapped[float | None] = mapped_column(Numeric(15, 2))
    deductions: Mapped[float | None] = mapped_column(Numeric(15, 2))
    taxable_income: Mapped[float | None] = mapped_column(Numeric(15, 2))
    tax_due: Mapped[float | None] = mapped_column(Numeric(15, 2))
    tax_paid: Mapped[float | None] = mapped_column(Numeric(15, 2))  # Credits/prepaid
    tax_underpaid: Mapped[float | None] = mapped_column(Numeric(15, 2))
    tax_overpaid: Mapped[float | None] = mapped_column(Numeric(15, 2))

    # Full calculation breakdown
    calculation_data: Mapped[dict | None] = mapped_column(JSON)

    # Filing metadata
    filing_reference: Mapped[str | None] = mapped_column(String(100))  # BPE number
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="tax_filings", foreign_keys=[user_id]
    )
    consultant: Mapped["User | None"] = relationship(foreign_keys=[consultant_id])
    documents: Mapped[list["Document"]] = relationship(back_populates="filing")
