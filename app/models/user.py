import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    TAXPAYER = "taxpayer"
    CONSULTANT = "consultant"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20), index=True)
    whatsapp_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    npwp: Mapped[str | None] = mapped_column(String(20), index=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.TAXPAYER
    )
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(back_populates="user")
    tax_filings: Mapped[list["TaxFiling"]] = relationship(back_populates="user")

    # Consultant-specific fields
    license_number: Mapped[str | None] = mapped_column(String(50))  # No. Izin Praktik
    license_level: Mapped[str | None] = mapped_column(String(1))  # A, B, or C
    max_clients: Mapped[int | None] = mapped_column()
