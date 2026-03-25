"""Tax calendar engine — compute all deadlines and send proactive reminders."""

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ObligationType(str, Enum):
    SPT_TAHUNAN_OP = "spt_tahunan_op"  # Orang Pribadi
    SPT_TAHUNAN_BADAN = "spt_tahunan_badan"
    SPT_MASA_PPN = "spt_masa_ppn"
    SPT_MASA_PPH21 = "spt_masa_pph21"
    SPT_MASA_PPH23 = "spt_masa_pph23"
    SPT_MASA_PPH25 = "spt_masa_pph25"
    SPT_MASA_PPH4_2 = "spt_masa_pph4_2"
    SPT_MASA_PPH22 = "spt_masa_pph22"
    EFAKTUR = "efaktur"
    EBUPOT = "ebupot"


class DeadlineStatus(str, Enum):
    UPCOMING = "upcoming"  # > 7 days away
    DUE_SOON = "due_soon"  # 1-7 days
    OVERDUE = "overdue"
    FILED = "filed"


@dataclass
class TaxDeadline:
    obligation: ObligationType
    label: str
    tax_period_month: int
    tax_period_year: int
    deadline_date: date
    payment_deadline: date
    status: DeadlineStatus
    days_remaining: int
    penalty_amount: float  # If missed
    penalty_description: str


# Deadline rules (day of month, relative to tax period)
DEADLINE_RULES = {
    ObligationType.SPT_TAHUNAN_OP: {
        "filing_month_offset": 3,  # March of next year
        "filing_day": 31,
        "payment_month_offset": 3,
        "payment_day": 31,
        "penalty": 100_000,
        "penalty_desc": "Denda Rp 100.000 (Pasal 7 UU KUP)",
    },
    ObligationType.SPT_TAHUNAN_BADAN: {
        "filing_month_offset": 4,  # April of next year
        "filing_day": 30,
        "payment_month_offset": 4,
        "payment_day": 30,
        "penalty": 1_000_000,
        "penalty_desc": "Denda Rp 1.000.000 (Pasal 7 UU KUP)",
    },
    ObligationType.SPT_MASA_PPN: {
        "filing_day_offset": 0,  # End of next month
        "filing_day": -1,  # Last day of month
        "payment_day": -1,
        "penalty": 500_000,
        "penalty_desc": "Denda Rp 500.000/bulan (Pasal 7 UU KUP)",
    },
    ObligationType.SPT_MASA_PPH21: {
        "filing_day": 20,  # 20th of next month
        "payment_day": 10,  # 10th of next month
        "penalty": 100_000,
        "penalty_desc": "Denda Rp 100.000/bulan + bunga 2%/bulan atas kurang bayar",
    },
    ObligationType.SPT_MASA_PPH23: {
        "filing_day": 20,
        "payment_day": 10,
        "penalty": 100_000,
        "penalty_desc": "Denda Rp 100.000/bulan",
    },
    ObligationType.SPT_MASA_PPH25: {
        "filing_day": 20,
        "payment_day": 15,
        "penalty": 100_000,
        "penalty_desc": "Denda Rp 100.000/bulan",
    },
    ObligationType.SPT_MASA_PPH4_2: {
        "filing_day": 20,
        "payment_day": 10,
        "penalty": 100_000,
        "penalty_desc": "Denda Rp 100.000/bulan",
    },
}


def _next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def _last_day(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


def compute_deadline(
    obligation: ObligationType,
    tax_period_month: int,
    tax_period_year: int,
    today: date | None = None,
) -> TaxDeadline:
    """Compute the filing and payment deadline for a tax obligation."""
    today = today or date.today()
    rule = DEADLINE_RULES.get(obligation)

    if not rule:
        # Default: 20th of next month
        ny, nm = _next_month(tax_period_year, tax_period_month)
        dl = date(ny, nm, 20)
        pay_dl = date(ny, nm, 10)
        penalty = 100_000
        penalty_desc = "Denda keterlambatan"
    elif "filing_month_offset" in rule:
        # Annual SPT
        dl_year = tax_period_year + 1
        dl_month = rule["filing_month_offset"]
        dl_day = min(rule["filing_day"], _last_day(dl_year, dl_month))
        dl = date(dl_year, dl_month, dl_day)
        pay_dl = dl
        penalty = rule["penalty"]
        penalty_desc = rule["penalty_desc"]
    else:
        # Monthly SPT Masa
        ny, nm = _next_month(tax_period_year, tax_period_month)
        filing_day = rule["filing_day"]
        if filing_day == -1:
            filing_day = _last_day(ny, nm)
        payment_day = rule["payment_day"]
        if payment_day == -1:
            payment_day = _last_day(ny, nm)
        dl = date(ny, nm, min(filing_day, _last_day(ny, nm)))
        pay_dl = date(ny, nm, min(payment_day, _last_day(ny, nm)))
        penalty = rule["penalty"]
        penalty_desc = rule["penalty_desc"]

    days_remaining = (dl - today).days
    if days_remaining < 0:
        status = DeadlineStatus.OVERDUE
    elif days_remaining <= 7:
        status = DeadlineStatus.DUE_SOON
    else:
        status = DeadlineStatus.UPCOMING

    label_map = {
        ObligationType.SPT_TAHUNAN_OP: "SPT Tahunan Orang Pribadi",
        ObligationType.SPT_TAHUNAN_BADAN: "SPT Tahunan Badan",
        ObligationType.SPT_MASA_PPN: "SPT Masa PPN",
        ObligationType.SPT_MASA_PPH21: "SPT Masa PPh 21",
        ObligationType.SPT_MASA_PPH23: "SPT Masa PPh 23",
        ObligationType.SPT_MASA_PPH25: "SPT Masa PPh 25",
        ObligationType.SPT_MASA_PPH4_2: "SPT Masa PPh 4(2)",
        ObligationType.SPT_MASA_PPH22: "SPT Masa PPh 22",
    }

    return TaxDeadline(
        obligation=obligation,
        label=label_map.get(obligation, obligation.value),
        tax_period_month=tax_period_month,
        tax_period_year=tax_period_year,
        deadline_date=dl,
        payment_deadline=pay_dl,
        status=status,
        days_remaining=days_remaining,
        penalty_amount=penalty,
        penalty_description=penalty_desc,
    )


def get_client_deadlines(
    obligations: list[ObligationType],
    filed_periods: set[tuple[str, int, int]] | None = None,
    today: date | None = None,
    months_ahead: int = 3,
) -> list[TaxDeadline]:
    """Get all upcoming deadlines for a client based on their obligation types."""
    today = today or date.today()
    filed_periods = filed_periods or set()
    deadlines = []

    for obligation in obligations:
        if "tahunan" in obligation.value:
            # Annual: check current and previous year
            for year in [today.year - 1, today.year]:
                dl = compute_deadline(obligation, 12, year, today)
                key = (obligation.value, year, 12)
                if key in filed_periods:
                    dl.status = DeadlineStatus.FILED
                if dl.status != DeadlineStatus.FILED and dl.days_remaining > -90:
                    deadlines.append(dl)
        else:
            # Monthly: generate for current + future months
            current_month = today.month
            current_year = today.year
            # Also check previous month (might be overdue)
            start_month = current_month - 1 if current_month > 1 else 12
            start_year = current_year if current_month > 1 else current_year - 1

            m, y = start_month, start_year
            for _ in range(months_ahead + 1):
                dl = compute_deadline(obligation, m, y, today)
                key = (obligation.value, y, m)
                if key in filed_periods:
                    dl.status = DeadlineStatus.FILED
                if dl.status != DeadlineStatus.FILED:
                    deadlines.append(dl)
                y, m = _next_month(y, m)

    deadlines.sort(key=lambda d: d.deadline_date)
    return deadlines


def format_deadline_whatsapp(deadline: TaxDeadline) -> str:
    """Format a deadline for WhatsApp notification."""
    emoji = {
        DeadlineStatus.OVERDUE: "🔴",
        DeadlineStatus.DUE_SOON: "🟡",
        DeadlineStatus.UPCOMING: "🟢",
        DeadlineStatus.FILED: "✅",
    }
    status_text = {
        DeadlineStatus.OVERDUE: f"TERLAMBAT {abs(deadline.days_remaining)} hari!",
        DeadlineStatus.DUE_SOON: f"Sisa {deadline.days_remaining} hari",
        DeadlineStatus.UPCOMING: f"Sisa {deadline.days_remaining} hari",
        DeadlineStatus.FILED: "Sudah dilaporkan",
    }

    period = f"{deadline.tax_period_month:02d}/{deadline.tax_period_year}"
    lines = [
        f"{emoji[deadline.status]} *{deadline.label}*",
        f"Masa: {period}",
        f"Deadline: {deadline.deadline_date.strftime('%d %B %Y')}",
        f"Status: {status_text[deadline.status]}",
    ]
    if deadline.status == DeadlineStatus.OVERDUE:
        lines.append(f"⚠️ Denda: Rp {deadline.penalty_amount:,.0f}")

    return "\n".join(lines)
