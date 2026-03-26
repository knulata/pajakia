"""Consent tracking — records when clients authorize consultant access."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ConsentType(str, enum.Enum):
    DATA_ACCESS = "data_access"
    DOCUMENT_PROCESSING = "document_processing"
    SPT_FILING = "spt_filing"
    WHATSAPP_COMMUNICATION = "whatsapp_communication"
    DATA_RETENTION = "data_retention"


class ConsentStatus(str, enum.Enum):
    GRANTED = "granted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ClientConsent(Base):
    __tablename__ = "client_consents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id"), index=True
    )
    consultant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    consent_type: Mapped[ConsentType] = mapped_column(SQLEnum(ConsentType))
    status: Mapped[ConsentStatus] = mapped_column(
        SQLEnum(ConsentStatus), default=ConsentStatus.GRANTED
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence: Mapped[str | None] = mapped_column(Text)

    # Relationships
    client: Mapped["Client"] = relationship(foreign_keys=[client_id])
    consultant: Mapped["User"] = relationship(foreign_keys=[consultant_id])
