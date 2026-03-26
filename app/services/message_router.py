"""Route incoming WhatsApp messages — auto-OCR, link to consultant clients."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.client import Client
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.whatsapp_message import WhatsAppMessage, MessageDirection, MessageType
from app.models.audit_log import AuditLog
from app.services import whatsapp
from app.services.document_store import store_document
from app.services.ocr import extract_bukti_potong, extract_faktur_pajak, detect_document_type

logger = logging.getLogger(__name__)

STATE_AWAITING_DOC_TYPE = "awaiting_doc_type"

WELCOME_MESSAGE = (
    "Halo! Selamat datang di Pajakia\n\n"
    "Saya asisten pajak digital Anda. Langsung kirim foto dokumen pajak — "
    "saya akan baca dan ekstrak datanya otomatis.\n\n"
    "Yang bisa saya proses:\n"
    "📄 Bukti Potong 1721-A1/A2\n"
    "🧾 Faktur Pajak\n"
    "📋 Bukti Potong PPh 23/26/4(2)\n"
    "📑 Dokumen PDF\n\n"
    "Kirim foto sekarang, atau ketik 'bantuan' untuk info lengkap."
)

HELP_MESSAGE = (
    "Cara pakai Pajakia via WhatsApp:\n\n"
    "1. *Foto dokumen* — Langsung kirim foto bukti potong, faktur pajak, "
    "atau dokumen pajak lainnya. AI akan baca dan ekstrak datanya.\n\n"
    "2. *Kirim PDF* — Kirim file PDF untuk diproses.\n\n"
    "3. *Cek deadline* — Ketik 'deadline'\n\n"
    "4. *Tanya pajak* — Ketik pertanyaan Anda\n\n"
    "Semua dokumen yang Anda kirim akan masuk ke dashboard konsultan pajak Anda "
    "(jika Anda terdaftar sebagai klien)."
)

DOC_TYPE_BUTTONS = [
    {"id": "doc_bp_a1", "title": "Bukti Potong A1"},
    {"id": "doc_bp_a2", "title": "Bukti Potong A2"},
    {"id": "doc_faktur", "title": "Faktur Pajak"},
]

DOC_TYPE_MAP = {
    "doc_bp_a1": DocumentType.BUKTI_POTONG_A1,
    "doc_bp_a2": DocumentType.BUKTI_POTONG_A2,
    "doc_faktur": DocumentType.FAKTUR_PAJAK,
    "doc_other": DocumentType.OTHER,
}


async def route_message(message: dict, db: AsyncSession) -> None:
    """Main entry point: route an incoming WhatsApp message."""
    phone = message["from"]
    msg_type = message["type"]

    user = await _get_or_create_user(phone, message.get("from_name", ""), db)

    # Log inbound message
    wa_msg = WhatsAppMessage(
        wa_message_id=message["id"],
        user_id=user.id,
        wa_from=phone,
        direction=MessageDirection.INBOUND,
        message_type=MessageType(msg_type) if msg_type in [e.value for e in MessageType] else MessageType.TEXT,
        body=message.get("text"),
        raw_payload=message,
    )
    db.add(wa_msg)

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
            "Orang Pribadi: 31 Maret 2026\n"
            "Badan: 30 April 2026\n\n"
            "📅 *SPT Masa (bulanan):*\n"
            "PPh 21/23/25: tanggal 20 bulan berikutnya\n"
            "PPN: akhir bulan berikutnya"
        )
    elif text == "status":
        # Show document processing status
        result = await db.execute(
            select(Document)
            .where(Document.user_id == user.id)
            .order_by(Document.created_at.desc())
            .limit(5)
        )
        docs = result.scalars().all()
        if docs:
            lines = ["📋 *Status dokumen terbaru:*\n"]
            for d in docs:
                status_emoji = {"uploaded": "⏳", "processing": "🔄", "extracted": "✅", "verified": "✅✅", "failed": "❌"}.get(d.status.value, "❓")
                lines.append(f"{status_emoji} {d.file_name} — {d.status.value}")
            await whatsapp.send_text_message(phone, "\n".join(lines))
        else:
            await whatsapp.send_text_message(phone, "Belum ada dokumen. Kirim foto bukti potong untuk memulai.")
    else:
        await whatsapp.send_text_message(
            phone,
            "Kirim foto dokumen pajak dan saya akan langsung proses.\n\n"
            "Atau ketik: 'deadline', 'status', atau 'bantuan'."
        )


async def _handle_image(user: User, message: dict, db: AsyncSession) -> None:
    """Handle incoming image — auto-detect type, run OCR, send results."""
    phone = message["from"]
    image_info = message.get("image", {})
    media_id = image_info.get("id")

    if not media_id:
        await whatsapp.send_text_message(phone, "Maaf, gambar tidak dapat diproses.")
        return

    # Acknowledge receipt immediately
    await whatsapp.send_text_message(
        phone, "📸 Foto diterima! Sedang memproses dengan AI..."
    )

    try:
        # Download the image
        content = await whatsapp.download_media(media_id)
        mime_type = image_info.get("mime_type", "image/jpeg")

        # Auto-detect document type
        detected_type = await detect_document_type(content, mime_type)
        doc_type = _map_detected_type(detected_type)

        # Store the document
        file_url = await store_document(
            content=content,
            filename=f"{doc_type.value}_{message['id'][:8]}.jpg",
            user_id=user.id,
            mime_type=mime_type,
        )

        # Create document record
        doc = Document(
            user_id=user.id,
            doc_type=doc_type,
            status=DocumentStatus.PROCESSING,
            file_url=file_url,
            file_name=f"{doc_type.value}.jpg",
            mime_type=mime_type,
            file_size=len(content),
        )
        db.add(doc)
        await db.flush()

        # Run OCR based on detected type
        if doc_type in (DocumentType.BUKTI_POTONG_A1, DocumentType.BUKTI_POTONG_A2):
            extracted = await extract_bukti_potong(content, mime_type)
        elif doc_type == DocumentType.FAKTUR_PAJAK:
            extracted = await extract_faktur_pajak(content, mime_type)
        else:
            extracted = await extract_bukti_potong(content, mime_type)  # Default to BP extraction

        # Update document with extracted data
        if extracted and "error" not in extracted:
            doc.extracted_data = extracted
            doc.status = DocumentStatus.EXTRACTED
            doc.ocr_confidence = _estimate_confidence(extracted)

            # Send formatted results back via WhatsApp
            summary = _format_extraction_summary(doc_type, extracted)
            await whatsapp.send_text_message(phone, summary)

            # Log audit
            db.add(AuditLog(
                user_id=user.id,
                action="whatsapp_ocr",
                resource_type="document",
                resource_id=doc.id,
                detail=f"Auto-OCR via WhatsApp: {doc_type.value}",
            ))

            # Notify consultant if this user is a client
            await _notify_consultant(user, doc, db)
        else:
            doc.status = DocumentStatus.FAILED
            error_msg = extracted.get("error", "Unknown error") if isinstance(extracted, dict) else "Parse error"
            await whatsapp.send_text_message(
                phone,
                f"⚠️ Maaf, AI tidak bisa membaca dokumen ini. Error: {error_msg}\n\n"
                "Tips:\n"
                "- Pastikan foto tidak blur\n"
                "- Pastikan seluruh dokumen terlihat\n"
                "- Cahaya cukup terang\n\n"
                "Silakan kirim ulang."
            )

    except Exception as e:
        logger.exception("Failed to process WhatsApp image: %s", e)
        await whatsapp.send_text_message(
            phone, "Maaf, terjadi kesalahan saat memproses foto. Silakan coba lagi."
        )


async def _handle_document_upload(user: User, message: dict, db: AsyncSession) -> None:
    """Handle incoming document file (PDF, etc.) — store and run OCR."""
    phone = message["from"]
    doc_info = message.get("document", {})
    media_id = doc_info.get("id")
    filename = doc_info.get("filename", "document.pdf")

    if not media_id:
        await whatsapp.send_text_message(phone, "Maaf, dokumen tidak dapat diproses.")
        return

    await whatsapp.send_text_message(phone, f"📄 Dokumen '{filename}' diterima! Sedang diproses...")

    try:
        content = await whatsapp.download_media(media_id)
        mime = doc_info.get("mime_type", "application/pdf")

        file_url = await store_document(
            content=content, filename=filename,
            user_id=user.id, mime_type=mime,
        )

        doc = Document(
            user_id=user.id,
            doc_type=DocumentType.OTHER,
            status=DocumentStatus.UPLOADED,
            file_url=file_url,
            file_name=filename,
            mime_type=mime,
            file_size=len(content),
        )
        db.add(doc)
        await db.flush()

        # If it's a PDF image, try OCR
        if mime.startswith("image/"):
            doc.status = DocumentStatus.PROCESSING
            extracted = await extract_bukti_potong(content, mime)
            if extracted and "error" not in extracted:
                doc.extracted_data = extracted
                doc.status = DocumentStatus.EXTRACTED
                doc.ocr_confidence = _estimate_confidence(extracted)
                summary = _format_extraction_summary(doc.doc_type, extracted)
                await whatsapp.send_text_message(phone, summary)
            else:
                doc.status = DocumentStatus.UPLOADED  # Keep as uploaded, consultant will handle
                await whatsapp.send_text_message(
                    phone,
                    f"✅ Dokumen '{filename}' berhasil disimpan.\n"
                    "Konsultan pajak Anda akan mereviewnya."
                )
        else:
            await whatsapp.send_text_message(
                phone,
                f"✅ Dokumen '{filename}' berhasil disimpan.\n"
                "Konsultan pajak Anda akan mereviewnya."
            )

        db.add(AuditLog(
            user_id=user.id, action="whatsapp_upload",
            resource_type="document", resource_id=doc.id,
            detail=f"Document upload via WhatsApp: {filename}",
        ))

        await _notify_consultant(user, doc, db)

    except Exception as e:
        logger.exception("Failed to process document: %s", e)
        await whatsapp.send_text_message(
            phone, "Maaf, terjadi kesalahan saat memproses dokumen. Silakan coba lagi."
        )


async def _handle_interactive(user: User, message: dict, db: AsyncSession) -> None:
    """Handle interactive button responses."""
    phone = message["from"]
    interactive = message.get("interactive", {})
    button_reply = interactive.get("button_reply", {})
    button_id = button_reply.get("id", "")

    if button_id in DOC_TYPE_MAP:
        doc_type = DOC_TYPE_MAP[button_id]

        # Find the most recent image from this user with pending state
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
                    status=DocumentStatus.PROCESSING,
                    file_url=file_url,
                    file_name=f"{doc_type.value}.jpg",
                    mime_type="image/jpeg",
                    file_size=len(content),
                )
                db.add(doc)
                await db.flush()

                # Run OCR
                if doc_type in (DocumentType.BUKTI_POTONG_A1, DocumentType.BUKTI_POTONG_A2):
                    extracted = await extract_bukti_potong(content, "image/jpeg")
                elif doc_type == DocumentType.FAKTUR_PAJAK:
                    extracted = await extract_faktur_pajak(content, "image/jpeg")
                else:
                    extracted = await extract_bukti_potong(content, "image/jpeg")

                if extracted and "error" not in extracted:
                    doc.extracted_data = extracted
                    doc.status = DocumentStatus.EXTRACTED
                    doc.ocr_confidence = _estimate_confidence(extracted)
                    summary = _format_extraction_summary(doc_type, extracted)
                    await whatsapp.send_text_message(phone, summary)
                else:
                    doc.status = DocumentStatus.UPLOADED
                    await whatsapp.send_text_message(
                        phone,
                        f"✅ {button_reply.get('title', 'Dokumen')} disimpan.\n"
                        "AI tidak dapat membaca semua data — konsultan Anda akan mereview manual."
                    )

                await _notify_consultant(user, doc, db)

            except Exception as e:
                logger.error("Failed to process image: %s", e)
                await whatsapp.send_text_message(phone, "Maaf, terjadi kesalahan. Silakan kirim ulang foto.")
        else:
            await whatsapp.send_text_message(phone, "Maaf, tidak ada foto yang tertunda. Silakan kirim ulang.")
    else:
        await whatsapp.send_text_message(phone, "Maaf, pilihan tidak dikenali.")


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def _map_detected_type(detected: str) -> DocumentType:
    """Map auto-detected type string to DocumentType enum."""
    mapping = {
        "1721-A1": DocumentType.BUKTI_POTONG_A1,
        "1721-a1": DocumentType.BUKTI_POTONG_A1,
        "1721-A2": DocumentType.BUKTI_POTONG_A2,
        "1721-a2": DocumentType.BUKTI_POTONG_A2,
        "faktur_pajak": DocumentType.FAKTUR_PAJAK,
        "bukti_potong_pph23": DocumentType.BUKTI_POTONG_PPH23,
        "bukti_potong_pph4_2": DocumentType.BUKTI_POTONG_PPH4_2,
    }
    return mapping.get(detected, DocumentType.OTHER)


def _estimate_confidence(extracted: dict) -> float:
    """Estimate OCR confidence based on null/missing fields."""
    if not extracted or not isinstance(extracted, dict):
        return 0.0
    total_fields = 0
    filled_fields = 0
    for key, value in extracted.items():
        if key in ("raw_text", "parse_error", "error"):
            continue
        if isinstance(value, dict):
            for k, v in value.items():
                total_fields += 1
                if v is not None and v != "" and v != 0:
                    filled_fields += 1
        else:
            total_fields += 1
            if value is not None and value != "" and value != 0:
                filled_fields += 1
    return round(filled_fields / max(total_fields, 1), 2)


def _format_extraction_summary(doc_type: DocumentType, data: dict) -> str:
    """Format extracted data into a WhatsApp-friendly summary."""
    if doc_type in (DocumentType.BUKTI_POTONG_A1, DocumentType.BUKTI_POTONG_A2):
        bruto = data.get("penghasilan_bruto", {})
        pph = data.get("perhitungan_pph", {})
        total_bruto = bruto.get("total_bruto", 0) if isinstance(bruto, dict) else 0
        pph_terutang = pph.get("pph21_terutang", 0) if isinstance(pph, dict) else 0
        pph_dipotong = pph.get("pph21_telah_dipotong", 0) if isinstance(pph, dict) else 0

        return (
            f"✅ *Bukti Potong berhasil dibaca!*\n\n"
            f"👤 Nama: {data.get('nama_penerima', '-')}\n"
            f"🏢 Pemotong: {data.get('nama_pemotong', '-')}\n"
            f"📅 Masa: {data.get('masa_pajak', '-')} / {data.get('tahun_pajak', '-')}\n"
            f"💼 NPWP: {data.get('npwp_penerima', '-')}\n\n"
            f"💰 *Penghasilan Bruto:* Rp {_fmt_num(total_bruto)}\n"
            f"📊 *PPh 21 Terutang:* Rp {_fmt_num(pph_terutang)}\n"
            f"✂️ *PPh 21 Dipotong:* Rp {_fmt_num(pph_dipotong)}\n\n"
            f"Status PTKP: {data.get('status_ptkp', '-')}\n"
            f"No. Bukti Potong: {data.get('nomor_bukti_potong', '-')}\n\n"
            "Data ini sudah tersimpan di dashboard. "
            "Konsultan pajak Anda akan mereview sebelum diproses ke SPT."
        )

    elif doc_type == DocumentType.FAKTUR_PAJAK:
        return (
            f"✅ *Faktur Pajak berhasil dibaca!*\n\n"
            f"📄 No. Seri: {data.get('nomor_seri', '-')}\n"
            f"🏢 Penjual: {data.get('nama_penjual', '-')}\n"
            f"🏪 Pembeli: {data.get('nama_pembeli', '-')}\n"
            f"📅 Tanggal: {data.get('tanggal', '-')}\n\n"
            f"💰 *DPP:* Rp {_fmt_num(data.get('dpp', 0))}\n"
            f"📊 *PPN:* Rp {_fmt_num(data.get('ppn', 0))}\n"
            f"📋 *Total:* Rp {_fmt_num(data.get('total', 0))}\n\n"
            "Data tersimpan. Konsultan Anda akan mereview."
        )

    else:
        return (
            "✅ *Dokumen berhasil dibaca!*\n\n"
            "Data tersimpan di dashboard. Konsultan pajak Anda akan mereview.\n\n"
            "Kirim dokumen lainnya, atau ketik 'status' untuk cek progress."
        )


def _fmt_num(n) -> str:
    """Format number with thousand separator."""
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(n) if n else "0"


async def _notify_consultant(user: User, doc: Document, db: AsyncSession) -> None:
    """If this user is a client of a consultant, notify the consultant via WhatsApp."""
    try:
        # Find if this user is linked to a consultant client
        result = await db.execute(
            select(Client).where(Client.user_id == user.id)
        )
        client = result.scalar_one_or_none()
        if not client:
            # Try matching by phone
            result = await db.execute(
                select(Client).where(
                    (Client.phone == user.phone) | (Client.whatsapp_id == user.whatsapp_id)
                )
            )
            client = result.scalar_one_or_none()

        if not client:
            return

        # Link user to client if not already linked
        if not client.user_id:
            client.user_id = user.id

        # Get consultant's user record
        consultant_result = await db.execute(
            select(User).where(User.id == client.consultant_id)
        )
        consultant = consultant_result.scalar_one_or_none()
        if not consultant or not consultant.phone:
            return

        # Send notification to consultant
        status_text = "data berhasil diekstrak AI" if doc.status == DocumentStatus.EXTRACTED else "perlu review manual"
        confidence_text = f" (confidence: {int(doc.ocr_confidence * 100)}%)" if doc.ocr_confidence else ""

        await whatsapp.send_text_message(
            consultant.phone,
            f"📬 *Dokumen baru dari klien!*\n\n"
            f"👤 Klien: {client.name}\n"
            f"📄 Tipe: {doc.doc_type.value}\n"
            f"📊 Status: {status_text}{confidence_text}\n\n"
            "Buka dashboard untuk review."
        )

    except Exception as e:
        # Don't fail the main flow if notification fails
        logger.warning("Failed to notify consultant: %s", e)


async def _get_or_create_user(phone: str, name: str, db: AsyncSession) -> User:
    """Find user by WhatsApp phone or create a new one."""
    result = await db.execute(
        select(User).where(
            (User.whatsapp_id == phone) | (User.phone == phone)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=f"{phone}@wa.pajakia.com",
            name=name or f"WA User {phone[-4:]}",
            phone=phone,
            whatsapp_id=phone,
        )
        db.add(user)
        await db.flush()
        logger.info("Created new user for WhatsApp %s: %s", phone, user.id)

    return user
