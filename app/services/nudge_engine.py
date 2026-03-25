"""Proactive nudge engine — send WhatsApp reminders before deadlines hit."""

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from app.services.tax_calendar import (
    ObligationType, get_client_deadlines, format_deadline_whatsapp, DeadlineStatus,
)
from app.services import whatsapp

logger = logging.getLogger(__name__)


@dataclass
class NudgeRule:
    days_before: int
    message_template: str
    include_penalty: bool = False
    include_billing_code: bool = False


# When to nudge, relative to deadline
NUDGE_SCHEDULE = [
    NudgeRule(
        days_before=7,
        message_template=(
            "📅 *Pengingat Pajak*\n\n"
            "{deadline_info}\n\n"
            "Masih ada waktu 7 hari. Perlu bantuan menyiapkan?"
        ),
    ),
    NudgeRule(
        days_before=3,
        message_template=(
            "⚠️ *Deadline Mendekat!*\n\n"
            "{deadline_info}\n\n"
            "Hanya 3 hari tersisa. Hindari denda — siapkan sekarang."
        ),
        include_penalty=True,
    ),
    NudgeRule(
        days_before=1,
        message_template=(
            "🔴 *BESOK DEADLINE!*\n\n"
            "{deadline_info}\n\n"
            "Besok terakhir. Jangan sampai kena denda!"
        ),
        include_penalty=True,
        include_billing_code=True,
    ),
    NudgeRule(
        days_before=0,
        message_template=(
            "🚨 *HARI INI TERAKHIR!*\n\n"
            "{deadline_info}\n\n"
            "Segera laporkan sebelum tengah malam."
        ),
        include_penalty=True,
        include_billing_code=True,
    ),
    NudgeRule(
        days_before=-1,
        message_template=(
            "🔴 *TERLAMBAT*\n\n"
            "{deadline_info}\n\n"
            "Deadline sudah lewat. Segera laporkan untuk meminimalkan denda.\n"
            "💰 Potensi denda: {penalty}"
        ),
        include_penalty=True,
    ),
]


async def check_and_send_nudges(
    clients: list[dict],
    today: date | None = None,
) -> list[dict]:
    """Check all clients for upcoming deadlines and send nudges.

    Each client dict: phone, name, obligations: list[str], filed_periods: set
    Returns list of sent nudges.
    """
    today = today or date.today()
    sent = []

    for client in clients:
        phone = client.get("phone") or client.get("whatsapp_id")
        if not phone:
            continue

        obligations = [
            ObligationType(o) for o in client.get("obligations", [])
            if o in [e.value for e in ObligationType]
        ]
        filed = set()
        for fp in client.get("filed_periods", []):
            filed.add(tuple(fp))

        deadlines = get_client_deadlines(
            obligations=obligations,
            filed_periods=filed,
            today=today,
            months_ahead=2,
        )

        for dl in deadlines:
            if dl.status == DeadlineStatus.FILED:
                continue

            for rule in NUDGE_SCHEDULE:
                if dl.days_remaining == rule.days_before:
                    deadline_info = format_deadline_whatsapp(dl)
                    message = rule.message_template.format(
                        deadline_info=deadline_info,
                        penalty=f"Rp {dl.penalty_amount:,.0f}",
                        client_name=client.get("name", ""),
                    )

                    try:
                        await whatsapp.send_text_message(phone, message)
                        sent.append({
                            "phone": phone,
                            "client_name": client.get("name"),
                            "obligation": dl.obligation.value,
                            "deadline": str(dl.deadline_date),
                            "days_remaining": dl.days_remaining,
                            "message_sent": True,
                        })
                        logger.info(
                            "Nudge sent to %s for %s (deadline: %s)",
                            phone, dl.label, dl.deadline_date,
                        )
                    except Exception as e:
                        logger.error("Failed to send nudge to %s: %s", phone, e)
                        sent.append({
                            "phone": phone,
                            "client_name": client.get("name"),
                            "obligation": dl.obligation.value,
                            "error": str(e),
                            "message_sent": False,
                        })
                    break  # Only send one nudge per deadline per run

    return sent


async def send_document_request(
    phone: str,
    client_name: str,
    doc_types: list[str],
    masa: int,
    tahun: int,
) -> dict:
    """Ask a client to send their documents via WhatsApp."""
    doc_labels = {
        "bukti_potong": "bukti potong",
        "faktur_pajak": "faktur pajak",
        "invoice": "invoice/tagihan",
        "bank_statement": "mutasi rekening",
        "payroll": "slip gaji",
    }

    docs = ", ".join(doc_labels.get(d, d) for d in doc_types)
    message = (
        f"Halo {client_name},\n\n"
        f"Untuk keperluan pelaporan pajak masa {masa:02d}/{tahun}, "
        f"mohon kirimkan dokumen berikut:\n\n"
        f"📄 {docs}\n\n"
        f"Cukup foto dan kirim ke chat ini. "
        f"Kami akan memproses otomatis.\n\n"
        f"Terima kasih! 🙏"
    )

    try:
        result = await whatsapp.send_text_message(phone, message)
        return {"status": "sent", "phone": phone, "result": result}
    except Exception as e:
        return {"status": "failed", "phone": phone, "error": str(e)}
