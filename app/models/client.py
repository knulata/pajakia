"""Client model — taxpayers managed by a consultant."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ONBOARDING = "onboarding"


class EntityType(str, Enum):
    ORANG_PRIBADI = "orang_pribadi"
    PT = "pt"
    CV = "cv"
    FIRMA = "firma"
    YAYASAN = "yayasan"
    KOPERASI = "koperasi"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    consultant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )

    # Client info
    name: Mapped[str] = mapped_column(String(255))
    npwp: Mapped[str | None] = mapped_column(String(20), index=True)
    nik: Mapped[str | None] = mapped_column(String(16))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    whatsapp_id: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(500))

    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType), default=EntityType.ORANG_PRIBADI
    )
    status: Mapped[ClientStatus] = mapped_column(
        SQLEnum(ClientStatus), default=ClientStatus.ACTIVE
    )
    is_pkp: Mapped[bool] = mapped_column(Boolean, default=False)

    # Tax profile
    ptkp_status: Mapped[str | None] = mapped_column(String(10))
    tax_obligations: Mapped[list | None] = mapped_column(JSON)  # List of ObligationType values
    monthly_revenue_estimate: Mapped[float | None] = mapped_column()

    # Engagement
    fee_monthly: Mapped[float | None] = mapped_column()
    fee_annual_spt: Mapped[float | None] = mapped_column()
    contract_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contract_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    consultant: Mapped["User"] = relationship(foreign_keys=[consultant_id])
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])
