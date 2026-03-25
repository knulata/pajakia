"""Tax anomaly detection — catch errors before DJP does."""

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    CRITICAL = "critical"  # Will cause rejection or penalty
    WARNING = "warning"  # Likely error, needs review
    INFO = "info"  # Unusual but possibly intentional


@dataclass
class Anomaly:
    code: str
    severity: Severity
    title: str
    description: str
    field: str
    expected: str
    actual: str
    suggestion: str


def detect_pph21_anomalies(
    gross_income: float,
    pph_dipotong: float,
    status_ptkp: str,
    biaya_jabatan: float,
    iuran_pensiun: float,
    neto: float,
    employer_name: str = "",
) -> list[Anomaly]:
    """Detect anomalies in PPh 21 / bukti potong data."""
    anomalies = []

    # 1. Biaya jabatan > 5% or > 6M
    expected_bj = min(gross_income * 0.05, 6_000_000)
    if biaya_jabatan > 0 and abs(biaya_jabatan - expected_bj) > 10_000:
        anomalies.append(Anomaly(
            code="BJ001",
            severity=Severity.WARNING,
            title="Biaya jabatan tidak sesuai",
            description=f"Biaya jabatan seharusnya 5% dari bruto (maks Rp 6 juta)",
            field="biaya_jabatan",
            expected=f"Rp {expected_bj:,.0f}",
            actual=f"Rp {biaya_jabatan:,.0f}",
            suggestion="Periksa kembali perhitungan biaya jabatan di bukti potong",
        ))

    # 2. Neto doesn't match bruto - pengurang
    expected_neto = gross_income - biaya_jabatan - iuran_pensiun
    if neto > 0 and abs(neto - expected_neto) > 10_000:
        anomalies.append(Anomaly(
            code="NET001",
            severity=Severity.CRITICAL,
            title="Penghasilan neto tidak cocok",
            description="Neto harus = Bruto - Biaya Jabatan - Iuran Pensiun",
            field="neto",
            expected=f"Rp {expected_neto:,.0f}",
            actual=f"Rp {neto:,.0f}",
            suggestion="Minta koreksi bukti potong ke pemberi kerja",
        ))

    # 3. PPh 21 rate sanity check
    if gross_income > 0 and pph_dipotong > 0:
        effective_rate = pph_dipotong / gross_income
        if effective_rate > 0.35:
            anomalies.append(Anomaly(
                code="RATE001",
                severity=Severity.CRITICAL,
                title="Tarif efektif PPh 21 terlalu tinggi",
                description=f"Tarif efektif {effective_rate*100:.1f}% melebihi tarif tertinggi 35%",
                field="pph_dipotong",
                expected="Maks 35% dari bruto",
                actual=f"{effective_rate*100:.1f}%",
                suggestion="Kemungkinan ada kesalahan perhitungan di bukti potong",
            ))
        elif effective_rate > 0.25 and gross_income < 500_000_000:
            anomalies.append(Anomaly(
                code="RATE002",
                severity=Severity.WARNING,
                title="Tarif efektif PPh 21 tampak tinggi",
                description=f"Tarif efektif {effective_rate*100:.1f}% untuk penghasilan bruto Rp {gross_income:,.0f}",
                field="pph_dipotong",
                expected="< 25% untuk bruto di bawah Rp 500 juta",
                actual=f"{effective_rate*100:.1f}%",
                suggestion="Periksa apakah status PTKP sudah benar",
            ))

    # 4. Zero tax on significant income
    if gross_income > 60_000_000 and pph_dipotong == 0:
        anomalies.append(Anomaly(
            code="ZERO001",
            severity=Severity.WARNING,
            title="PPh 21 nihil untuk penghasilan > Rp 60 juta",
            description="Penghasilan bruto di atas PTKP tertinggi tapi PPh nihil",
            field="pph_dipotong",
            expected="> Rp 0",
            actual="Rp 0",
            suggestion="Periksa apakah PTKP status benar atau ada kompensasi kerugian",
        ))

    # 5. PTKP status validation
    valid_statuses = ["TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3",
                      "K/I/0", "K/I/1", "K/I/2", "K/I/3"]
    if status_ptkp and status_ptkp not in valid_statuses:
        anomalies.append(Anomaly(
            code="PTKP001",
            severity=Severity.CRITICAL,
            title="Status PTKP tidak valid",
            description=f"Status '{status_ptkp}' bukan status PTKP yang diakui",
            field="status_ptkp",
            expected="TK/0, TK/1, ..., K/3, K/I/0, ..., K/I/3",
            actual=status_ptkp,
            suggestion="Perbaiki status PTKP sesuai kondisi keluarga",
        ))

    return anomalies


def detect_ppn_anomalies(
    dpp: float,
    ppn: float,
    ppn_rate: float = 0.11,
) -> list[Anomaly]:
    """Detect anomalies in PPN/VAT data."""
    anomalies = []

    expected_ppn = dpp * ppn_rate
    if abs(ppn - expected_ppn) > 100:
        anomalies.append(Anomaly(
            code="PPN001",
            severity=Severity.CRITICAL,
            title="PPN tidak sesuai dengan DPP",
            description=f"PPN seharusnya {ppn_rate*100:.0f}% dari DPP",
            field="ppn",
            expected=f"Rp {expected_ppn:,.0f}",
            actual=f"Rp {ppn:,.0f}",
            suggestion="Periksa tarif PPN (11% efektif 2022, 12% efektif 2025 untuk barang mewah)",
        ))

    if dpp < 0:
        anomalies.append(Anomaly(
            code="DPP001",
            severity=Severity.CRITICAL,
            title="DPP negatif",
            description="Dasar Pengenaan Pajak tidak boleh negatif",
            field="dpp",
            expected=">= 0",
            actual=f"Rp {dpp:,.0f}",
            suggestion="Periksa faktur pajak — mungkin ada retur yang belum diproses",
        ))

    return anomalies


def detect_cross_filing_anomalies(
    filings: list[dict],
) -> list[Anomaly]:
    """Detect anomalies across multiple filings for the same taxpayer."""
    anomalies = []

    # Check for duplicate filing periods
    periods = {}
    for f in filings:
        key = (f.get("filing_type"), f.get("tax_year"), f.get("tax_month"))
        if key in periods:
            anomalies.append(Anomaly(
                code="DUP001",
                severity=Severity.WARNING,
                title="Duplikasi periode pelaporan",
                description=f"Ditemukan 2 filing untuk {key}",
                field="filing_period",
                expected="1 filing per periode",
                actual="2+ filings",
                suggestion="Salah satu mungkin pembetulan — periksa nomor pembetulan",
            ))
        periods[key] = f

    # Check YoY income swing > 50%
    annual_filings = [f for f in filings if f.get("tax_month") is None]
    annual_filings.sort(key=lambda x: x.get("tax_year", 0))
    for i in range(1, len(annual_filings)):
        prev = annual_filings[i - 1].get("gross_income", 0)
        curr = annual_filings[i].get("gross_income", 0)
        if prev > 0 and curr > 0:
            change = (curr - prev) / prev
            if abs(change) > 0.5:
                direction = "naik" if change > 0 else "turun"
                anomalies.append(Anomaly(
                    code="YOY001",
                    severity=Severity.INFO,
                    title=f"Penghasilan {direction} {abs(change)*100:.0f}% YoY",
                    description=f"Penghasilan bruto {direction} signifikan dari tahun {annual_filings[i-1].get('tax_year')} ke {annual_filings[i].get('tax_year')}",
                    field="gross_income",
                    expected=f"Rp {prev:,.0f} (tahun lalu)",
                    actual=f"Rp {curr:,.0f} (tahun ini)",
                    suggestion="Pastikan perubahan ini benar — DJP mungkin akan meminta penjelasan",
                ))

    return anomalies
