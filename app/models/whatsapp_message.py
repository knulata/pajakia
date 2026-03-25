import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    REACTION = "reaction"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), index=True
    )
    wa_message_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    wa_from: Mapped[str] = mapped_column(String(20), index=True)  # Phone number
    wa_to: Mapped[str | None] = mapped_column(String(20))
    direction: Mapped[MessageDirection] = mapped_column(SQLEnum(MessageDirection))
    message_type: Mapped[MessageType] = mapped_column(SQLEnum(MessageType))
    body: Mapped[str | None] = mapped_column(Text)
    media_url: Mapped[str | None] = mapped_column(String(500))
    raw_payload: Mapped[dict | None] = mapped_column(JSON)

    # Conversation context
    context_message_id: Mapped[str | None] = mapped_column(String(100))
    conversation_state: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
