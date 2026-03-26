"""Document verification model — tracks OCR review, corrections, and approval."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DocumentVerification(Base):
    """Tracks the review and correction history of an OCR-extracted document."""
    __tablename__ = "document_verifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id"), unique=True, index=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )

    # Original OCR output vs corrected data
    original_data: Mapped[dict | None] = mapped_column(JSON)
    corrected_data: Mapped[dict | None] = mapped_column(JSON)
    field_corrections: Mapped[list | None] = mapped_column(JSON)

    # Verification status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewer_notes: Mapped[str | None] = mapped_column(Text)

    # Confidence tracking
    low_confidence_fields: Mapped[list | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    document: Mapped["Document"] = relationship(foreign_keys=[document_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewer_id])
