"""PPh 21 Tax Calculator — TER method (effective Jan 2024) + progressive rates."""

from dataclasses import dataclass
from enum import Enum


class PTKPStatus(str, Enum):
    TK0 = "TK/0"  # Single, no dependents
    TK1 = "TK/1"
    TK2 = "TK/2"
    TK3 = "TK/3"
    K0 = "K/0"  # Married, no dependents
    K1 = "K/1"
    K2 = "K/2"
    K3 = "K/3"
    KI0 = "K/I/0"  # Married, spouse's income combined
    KI1 = "K/I/1"
    KI2 = "K/I/2"
    KI3 = "K/I/3"


# PTKP values (Penghasilan Tidak Kena Pajak) — annual
PTKP = {
    PTKPStatus.TK0: 54_000_000,
    PTKPStatus.TK1: 58_500_000,
    PTKPStatus.TK2: 63_000_000,
    PTKPStatus.TK3: 67_500_000,
    PTKPStatus.K0: 58_500_000,
    PTKPStatus.K1: 63_000_000,
    PTKPStatus.K2: 67_500_000,
    PTKPStatus.K3: 72_000_000,
    PTKPStatus.KI0: 112_500_000,
    PTKPStatus.KI1: 117_000_000,
    PTKPStatus.KI2: 121_500_000,
    PTKPStatus.KI3: 126_000_000,
}

# Progressive tax brackets (UU HPP, effective 2022+)
BRACKETS = [
    (60_000_000, 0.05),
    (250_000_000, 0.15),
    (500_000_000, 0.25),
    (5_000_000_000, 0.30),
    (float("inf"), 0.35),
]

# TER (Tarif Efektif Rata-rata) monthly rates — PP 58/2023
# Category A: TK/0, TK/1
# Category B: TK/2, TK/3, K/0, K/1
# Category C: K/2, K/3, K/I/0, K/I/1, K/I/2, K/I/3
TER_CATEGORY = {
    PTKPStatus.TK0: "A", PTKPStatus.TK1: "A",
    PTKPStatus.TK2: "B", PTKPStatus.TK3: "B",
    PTKPStatus.K0: "B", PTKPStatus.K1: "B",
    PTKPStatus.K2: "C", PTKPStatus.K3: "C",
    PTKPStatus.KI0: "C", PTKPStatus.KI1: "C",
    PTKPStatus.KI2: "C", PTKPStatus.KI3: "C",
}

# TER monthly rates by category — (threshold, rate)
TER_RATES = {
    "A": [
        (5_400_000, 0.00),
        (5_650_000, 0.0025),
        (5_950_000, 0.005),
        (6_300_000, 0.0075),
        (6_750_000, 0.01),
        (7_500_000, 0.0125),
        (8_550_000, 0.015),
        (9_650_000, 0.0175),
        (10_050_000, 0.02),
        (10_350_000, 0.0225),
        (10_700_000, 0.025),
        (11_050_000, 0.03),
        (11_600_000, 0.035),
        (12_500_000, 0.04),
        (13_750_000, 0.045),
        (15_100_000, 0.05),
        (16_950_000, 0.06),
        (19_750_000, 0.07),
        (24_150_000, 0.08),
        (26_450_000, 0.09),
        (28_000_000, 0.10),
        (30_050_000, 0.11),
        (32_400_000, 0.12),
        (35_400_000, 0.13),
        (39_100_000, 0.14),
        (43_850_000, 0.15),
        (47_800_000, 0.16),
        (51_400_000, 0.17),
        (56_300_000, 0.18),
        (62_200_000, 0.19),
        (68_600_000, 0.20),
        (77_500_000, 0.21),
        (89_000_000, 0.22),
        (103_000_000, 0.23),
        (125_000_000, 0.24),
        (157_000_000, 0.25),
        (206_000_000, 0.26),
        (337_000_000, 0.27),
        (454_000_000, 0.28),
        (550_000_000, 0.29),
        (695_000_000, 0.30),
        (910_000_000, 0.31),
        (1_400_000_000, 0.32),
        (float("inf"), 0.34),
    ],
    "B": [
        (6_200_000, 0.00),
        (6_500_000, 0.0025),
        (6_850_000, 0.005),
        (7_300_000, 0.0075),
        (9_200_000, 0.01),
        (10_750_000, 0.015),
        (11_250_000, 0.02),
        (11_600_000, 0.025),
        (12_600_000, 0.03),
        (13_600_000, 0.035),
        (14_950_000, 0.04),
        (16_400_000, 0.045),
        (18_450_000, 0.05),
        (21_850_000, 0.06),
        (26_000_000, 0.07),
        (27_700_000, 0.08),
        (29_350_000, 0.09),
        (31_450_000, 0.10),
        (33_950_000, 0.11),
        (37_100_000, 0.12),
        (41_100_000, 0.13),
        (45_800_000, 0.14),
        (49_500_000, 0.15),
        (53_800_000, 0.16),
        (58_500_000, 0.17),
        (64_000_000, 0.18),
        (71_000_000, 0.19),
        (80_000_000, 0.20),
        (93_000_000, 0.21),
        (109_000_000, 0.22),
        (129_000_000, 0.23),
        (163_000_000, 0.24),
        (211_000_000, 0.25),
        (374_000_000, 0.26),
        (459_000_000, 0.27),
        (555_000_000, 0.28),
        (704_000_000, 0.29),
        (957_000_000, 0.30),
        (1_405_000_000, 0.31),
        (float("inf"), 0.33),
    ],
    "C": [
        (6_600_000, 0.00),
        (6_950_000, 0.0025),
        (7_350_000, 0.005),
        (7_800_000, 0.0075),
        (8_850_000, 0.01),
        (9_800_000, 0.0125),
        (10_950_000, 0.015),
        (11_200_000, 0.0175),
        (12_050_000, 0.02),
        (12_950_000, 0.025),
        (14_150_000, 0.03),
        (15_550_000, 0.035),
        (17_050_000, 0.04),
        (19_500_000, 0.045),
        (22_700_000, 0.05),
        (26_600_000, 0.06),
        (28_100_000, 0.07),
        (30_100_000, 0.08),
        (32_600_000, 0.09),
        (35_400_000, 0.10),
        (38_900_000, 0.11),
        (43_000_000, 0.12),
        (47_000_000, 0.13),
        (51_200_000, 0.14),
        (55_800_000, 0.15),
        (60_400_000, 0.16),
        (66_700_000, 0.17),
        (74_500_000, 0.18),
        (83_200_000, 0.19),
        (95_600_000, 0.20),
        (110_000_000, 0.21),
        (134_000_000, 0.22),
        (169_000_000, 0.23),
        (221_000_000, 0.24),
        (390_000_000, 0.25),
        (463_000_000, 0.26),
        (561_000_000, 0.27),
        (709_000_000, 0.28),
        (965_000_000, 0.29),
        (1_419_000_000, 0.30),
        (float("inf"), 0.32),
    ],
}


@dataclass
class TaxResult:
    gross_income: float
    ptkp_status: str
    ptkp_amount: float
    biaya_jabatan: float
    iuran_pensiun: float
    net_income: float
    taxable_income: float
    tax_due: float
    tax_paid: float  # Credits from bukti potong
    tax_underpaid: float
    tax_overpaid: float
    bracket_breakdown: list[dict]
    effective_rate: float
    calculation_formula: str


def calculate_pph21_annual(
    gross_income: float,
    ptkp_status: PTKPStatus = PTKPStatus.TK0,
    biaya_jabatan: float | None = None,
    iuran_pensiun: float = 0,
    tax_paid: float = 0,
) -> TaxResult:
    """Calculate annual PPh 21 using progressive rates (for SPT Tahunan)."""

    # Biaya jabatan: 5% of gross, max 6M/year
    if biaya_jabatan is None:
        biaya_jabatan = min(gross_income * 0.05, 6_000_000)

    ptkp_amount = PTKP[ptkp_status]

    net_income = gross_income - biaya_jabatan - iuran_pensiun
    taxable_income = max(0, net_income - ptkp_amount)

    # Apply progressive brackets
    tax_due = 0.0
    remaining = taxable_income
    breakdown = []
    prev_limit = 0

    for limit, rate in BRACKETS:
        bracket_size = limit - prev_limit
        taxable_in_bracket = min(remaining, bracket_size)
        if taxable_in_bracket <= 0:
            break
        tax_in_bracket = taxable_in_bracket * rate
        tax_due += tax_in_bracket
        breakdown.append({
            "bracket": f"Rp {prev_limit:,.0f} - Rp {limit:,.0f}" if limit != float("inf") else f"> Rp {prev_limit:,.0f}",
            "rate": f"{rate * 100:.0f}%",
            "taxable_amount": taxable_in_bracket,
            "tax": tax_in_bracket,
        })
        remaining -= taxable_in_bracket
        prev_limit = limit

    tax_underpaid = max(0, tax_due - tax_paid)
    tax_overpaid = max(0, tax_paid - tax_due)
    effective_rate = (tax_due / gross_income * 100) if gross_income > 0 else 0

    formula = (
        f"Penghasilan Bruto: Rp {gross_income:,.0f}\n"
        f"- Biaya Jabatan (5%, maks 6jt): Rp {biaya_jabatan:,.0f}\n"
        f"- Iuran Pensiun: Rp {iuran_pensiun:,.0f}\n"
        f"= Penghasilan Neto: Rp {net_income:,.0f}\n"
        f"- PTKP ({ptkp_status.value}): Rp {ptkp_amount:,.0f}\n"
        f"= PKP (Penghasilan Kena Pajak): Rp {taxable_income:,.0f}\n"
        f"PPh 21 Terutang: Rp {tax_due:,.0f}\n"
        f"PPh 21 Telah Dipotong: Rp {tax_paid:,.0f}\n"
        f"{'Kurang Bayar' if tax_underpaid > 0 else 'Lebih Bayar'}: "
        f"Rp {tax_underpaid if tax_underpaid > 0 else tax_overpaid:,.0f}"
    )

    return TaxResult(
        gross_income=gross_income,
        ptkp_status=ptkp_status.value,
        ptkp_amount=ptkp_amount,
        biaya_jabatan=biaya_jabatan,
        iuran_pensiun=iuran_pensiun,
        net_income=net_income,
        taxable_income=taxable_income,
        tax_due=tax_due,
        tax_paid=tax_paid,
        tax_underpaid=tax_underpaid,
        tax_overpaid=tax_overpaid,
        bracket_breakdown=breakdown,
        effective_rate=round(effective_rate, 2),
        calculation_formula=formula,
    )


def calculate_pph21_monthly_ter(
    monthly_gross: float,
    ptkp_status: PTKPStatus = PTKPStatus.TK0,
) -> dict:
    """Calculate monthly PPh 21 using TER method (Jan-Nov)."""
    category = TER_CATEGORY[ptkp_status]
    rates = TER_RATES[category]

    ter_rate = 0.0
    for threshold, rate in rates:
        if monthly_gross <= threshold:
            ter_rate = rate
            break

    tax = round(monthly_gross * ter_rate)

    return {
        "monthly_gross": monthly_gross,
        "ter_category": category,
        "ter_rate": ter_rate,
        "ter_rate_pct": f"{ter_rate * 100:.2f}%",
        "monthly_tax": tax,
        "ptkp_status": ptkp_status.value,
    }


def calculate_pph21_december(
    annual_gross: float,
    ptkp_status: PTKPStatus,
    total_ter_paid_jan_nov: float,
    iuran_pensiun: float = 0,
) -> dict:
    """Calculate December PPh 21 — true-up using progressive rates."""
    annual = calculate_pph21_annual(
        gross_income=annual_gross,
        ptkp_status=ptkp_status,
        iuran_pensiun=iuran_pensiun,
        tax_paid=0,
    )
    december_tax = max(0, annual.tax_due - total_ter_paid_jan_nov)

    return {
        "annual_tax_due": annual.tax_due,
        "total_ter_paid_jan_nov": total_ter_paid_jan_nov,
        "december_tax": december_tax,
        "difference": annual.tax_due - total_ter_paid_jan_nov,
        "annual_breakdown": annual.bracket_breakdown,
    }
