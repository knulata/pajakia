"""Portal token model — token-based access for client self-service document upload."""

import uuid
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy import String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _default_expiry():
    return datetime.now(timezone.utc) + timedelta(days=30)


class PortalToken(Base):
    """Unique token for each client to access their self-service upload portal.

    No login required — the token URL is the authentication.
    Consultants generate these and share with clients.
    """
    __tablename__ = "portal_tokens"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, default=lambda: secrets.token_urlsafe(48)
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id"), index=True
    )
    consultant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )

    # What documents are needed
    required_documents: Mapped[list | None] = mapped_column(JSON)
    tax_year: Mapped[int | None] = mapped_column()
    tax_month: Mapped[int | None] = mapped_column()

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_default_expiry
    )
    last_accessed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    client: Mapped["Client"] = relationship(foreign_keys=[client_id])
    consultant: Mapped["User"] = relationship(foreign_keys=[consultant_id])
