"""Coretax submission model — track XML uploads, retries, and Coretax references."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    QUEUED = "queued"           # In retry queue, not yet attempted
    UPLOADING = "uploading"     # Currently being sent to Coretax
    RETRYING = "retrying"       # Failed, scheduled for retry
    SUCCEEDED = "succeeded"     # Coretax accepted
    FAILED = "failed"           # Max retries exceeded
    CANCELLED = "cancelled"     # User cancelled


class SubmissionType(str, enum.Enum):
    EBUPOT = "ebupot"
    EFAKTUR = "efaktur"
    SPT_MASA_PPH21 = "spt_masa_pph21"
    SPT_MASA_PPH23 = "spt_masa_pph23"
    SPT_TAHUNAN_OP = "spt_tahunan_op"
    SPT_TAHUNAN_BADAN = "spt_tahunan_badan"


class CoretaxSubmission(Base):
    __tablename__ = "coretax_submissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    client_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("clients.id"), index=True
    )

    submission_type: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus), default=SubmissionStatus.QUEUED, index=True
    )

    # The XML payload (compressed in production, plain for now)
    xml_content: Mapped[str] = mapped_column(Text)

    # Tax period
    masa: Mapped[int] = mapped_column(Integer)
    tahun: Mapped[int] = mapped_column(Integer)

    # Retry state
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)

    # Result
    coretax_reference: Mapped[str | None] = mapped_column(String(100))  # BPE / receipt no
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    client: Mapped["Client | None"] = relationship(foreign_keys=[client_id])
