"""Route incoming WhatsApp messages to the appropriate handler."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.whatsapp_message import WhatsAppMessage, MessageDirection, MessageType
from app.services import whatsapp
from app.services.document_store import store_document

logger = logging.getLogger(__name__)

# Conversation states
STATE_IDLE = "idle"
STATE_AWAITING_DOC_TYPE = "awaiting_doc_type"
STATE_AWAITING_DOCUMENT = "awaiting_document"
STATE_REVIEWING_DATA = "reviewing_data"


WELCOME_MESSAGE = (
    "Halo! Selamat datang di PajakAI 🇮🇩\n\n"
    "Saya asisten pajak digital Anda. Saya bisa membantu:\n\n"
    "📄 Siapkan SPT Tahunan\n"
    "📸 Scan bukti potong\n"
    "❓ Jawab pertanyaan pajak\n\n"
    "Kirim foto bukti potong Anda untuk memulai, atau ketik 'bantuan' untuk info lebih lanjut."
)

HELP_MESSAGE = (
    "Berikut yang bisa saya bantu:\n\n"
    "1️⃣ *Foto Bukti Potong* — Kirim foto 1721-A1/A2, saya akan ekstrak datanya\n"
    "2️⃣ *Hitung PPh 21* — Ketik penghasilan bruto Anda\n"
    "3️⃣ *Cek Deadline* — Ketik 'deadline' untuk lihat batas waktu\n"
    "4️⃣ *Tanya Pajak* — Tanyakan apa saja tentang pajak Indonesia\n\n"
    "Ketik 'mulai' untuk memulai pembuatan SPT."
)

DOC_TYPE_BUTTONS = [
    {"id": "doc_bp_a1", "title": "Bukti Potong A1"},
    {"id": "doc_bp_a2", "title": "Bukti Potong A2"},
    {"id": "doc_other", "title": "Dokumen Lain"},
]

DOC_TYPE_MAP = {
    "doc_bp_a1": DocumentType.BUKTI_POTONG_A1,
    "doc_bp_a2": DocumentType.BUKTI_POTONG_A2,
    "doc_other": DocumentType.OTHER,
}


async def route_message(message: dict, db: AsyncSession) -> None:
    """Main entry point: route an incoming WhatsApp message."""
    phone = message["from"]
    msg_type = message["type"]

    # Find or create user
    user = await _get_or_create_user(phone, message.get("from_name", ""), db)

    # Log inbound message
    wa_msg = WhatsAppMessage(
        wa_message_id=message["id"],
        user_id=user.id,
        wa_from=phone,
        direction=MessageDirection.INBOUND,
        message_type=MessageType(msg_type) if msg_type in MessageType.__members__.values() else MessageType.TEXT,
        body=message.get("text"),
        raw_payload=message,
    )
    db.add(wa_msg)

    # Route by message type
    if msg_type == "text":
        await _handle_text(user, message, db)
    elif msg_type == "image":
        await _handle_image(user, message, db)
    elif msg_type == "document":
        await _handle_document_upload(user, message, db)
    elif msg_type == "interactive":
        await _handle_interactive(user, message, db)
    else:
        await whatsapp.send_text_message(
            phone, "Maaf, saya belum bisa memproses jenis pesan ini. Kirim foto atau teks."
        )

    await db.commit()


async def _handle_text(user: User, message: dict, db: AsyncSession) -> None:
    """Handle incoming text messages."""
    text = (message.get("text") or "").strip().lower()
    phone = message["from"]

    if text in ("hi", "halo", "hello", "start", "mulai"):
        await whatsapp.send_text_message(phone, WELCOME_MESSAGE)
    elif text in ("bantuan", "help", "menu"):
        await whatsapp.send_text_message(phone, HELP_MESSAGE)
    elif text == "deadline":
        await whatsapp.send_text_message(
            phone,
            "📅 *Deadline SPT Tahunan 2025:*\n\n"
            "• Orang Pribadi: 31 Maret 2026\n"
            "• Badan: 30 April 2026\n\n"
            "📅 *SPT Masa (bulanan):*\n"
            "• PPh 21/23/25: tanggal 20 bulan berikutnya\n"
            "• PPN: akhir bulan berikutnya"
        )
    else:
        # TODO: Route to AI Q&A service (Sprint 2)
        await whatsapp.send_text_message(
            phone,
            "Terima kasih atas pertanyaan Anda. Fitur tanya-jawab AI sedang dalam pengembangan.\n\n"
            "Untuk saat ini, kirim foto bukti potong Anda dan saya akan membantu ekstrak datanya."
        )


async def _handle_image(user: User, message: dict, db: AsyncSession) -> None:
    """Handle incoming image (photo of bukti potong, etc.)."""
    phone = message["from"]
    image_info = message.get("image", {})
    media_id = image_info.get("id")

    if not media_id:
        await whatsapp.send_text_message(phone, "Maaf, gambar tidak dapat diproses.")
        return

    # Ask what type of document this is
    await whatsapp.send_interactive_buttons(
        to=phone,
        body_text="Foto diterima! Jenis dokumen apa ini?",
        buttons=DOC_TYPE_BUTTONS,
        header="📄 Identifikasi Dokumen",
    )

    # Store media ID temporarily in conversation state
    # We'll process it when user selects document type
    user.whatsapp_id = phone  # Ensure WA ID is saved
    # Store pending media in a simple way — we'll use Redis for this in production
    wa_msg = await db.execute(
        select(WhatsAppMessage)
        .where(WhatsAppMessage.wa_message_id == message["id"])
    )
    msg_record = wa_msg.scalar_one_or_none()
    if msg_record:
        msg_record.conversation_state = STATE_AWAITING_DOC_TYPE
        msg_record.media_url = media_id  # Temporarily store media_id here


async def _handle_document_upload(user: User, message: dict, db: AsyncSession) -> None:
    """Handle incoming document file (PDF, etc.)."""
    phone = message["from"]
    doc_info = message.get("document", {})
    media_id = doc_info.get("id")
    filename = doc_info.get("filename", "document")

    if not media_id:
        await whatsapp.send_text_message(phone, "Maaf, dokumen tidak dapat diproses.")
        return

    # Download and store
    try:
        content = await whatsapp.download_media(media_id)
        file_url = await store_document(
            content=content,
            filename=filename,
            user_id=user.id,
            mime_type=doc_info.get("mime_type", "application/pdf"),
        )

        doc = Document(
            user_id=user.id,
            doc_type=DocumentType.OTHER,
            status=DocumentStatus.UPLOADED,
            file_url=file_url,
            file_name=filename,
            mime_type=doc_info.get("mime_type", "application/pdf"),
            file_size=len(content),
        )
        db.add(doc)

        await whatsapp.send_text_message(
            phone,
            f"✅ Dokumen '{filename}' berhasil diterima dan disimpan.\n\n"
            "Dokumen akan segera diproses. Anda akan menerima notifikasi setelah selesai."
        )
    except Exception as e:
        logger.error("Failed to process document: %s", e)
        await whatsapp.send_text_message(
            phone, "Maaf, terjadi kesalahan saat memproses dokumen. Silakan coba lagi."
        )


async def _handle_interactive(user: User, message: dict, db: AsyncSession) -> None:
    """Handle interactive button/list responses."""
    phone = message["from"]
    interactive = message.get("interactive", {})
    button_reply = interactive.get("button_reply", {})
    button_id = button_reply.get("id", "")

    if button_id in DOC_TYPE_MAP:
        doc_type = DOC_TYPE_MAP[button_id]

        # Find the most recent image message from this user with pending state
        result = await db.execute(
            select(WhatsAppMessage)
            .where(
                WhatsAppMessage.wa_from == phone,
                WhatsAppMessage.conversation_state == STATE_AWAITING_DOC_TYPE,
            )
            .order_by(WhatsAppMessage.created_at.desc())
            .limit(1)
        )
        pending_msg = result.scalar_one_or_none()

        if pending_msg and pending_msg.media_url:
            media_id = pending_msg.media_url
            pending_msg.conversation_state = None

            try:
                content = await whatsapp.download_media(media_id)
                file_url = await store_document(
                    content=content,
                    filename=f"{doc_type.value}.jpg",
                    user_id=user.id,
                    mime_type="image/jpeg",
                )

                doc = Document(
                    user_id=user.id,
                    doc_type=doc_type,
                    status=DocumentStatus.UPLOADED,
                    file_url=file_url,
                    file_name=f"{doc_type.value}.jpg",
                    mime_type="image/jpeg",
                    file_size=len(content),
                )
                db.add(doc)

                await whatsapp.send_text_message(
                    phone,
                    f"✅ {button_reply.get('title', 'Dokumen')} berhasil disimpan!\n\n"
                    "Sedang memproses... Anda akan menerima hasil ekstraksi dalam beberapa saat."
                )

                # TODO: Trigger OCR pipeline (Sprint 2)

            except Exception as e:
                logger.error("Failed to process image: %s", e)
                await whatsapp.send_text_message(
                    phone, "Maaf, terjadi kesalahan. Silakan kirim ulang foto."
                )
        else:
            await whatsapp.send_text_message(
                phone, "Maaf, saya tidak menemukan foto yang tertunda. Silakan kirim ulang."
            )
    else:
        await whatsapp.send_text_message(
            phone, "Maaf, pilihan tidak dikenali. Silakan coba lagi."
        )


async def _get_or_create_user(
    phone: str, name: str, db: AsyncSession
) -> User:
    """Find user by WhatsApp phone or create a new one."""
    result = await db.execute(
        select(User).where(
            (User.whatsapp_id == phone) | (User.phone == phone)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=f"{phone}@wa.pajakai.id",  # Placeholder until they register
            name=name or f"WA User {phone[-4:]}",
            phone=phone,
            whatsapp_id=phone,
        )
        db.add(user)
        await db.flush()
        logger.info("Created new user for WhatsApp %s: %s", phone, user.id)

    return user
