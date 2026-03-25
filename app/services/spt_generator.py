"""SPT Tahunan generator — produces structured SPT data and PDF for filing."""

import io
import logging
from dataclasses import dataclass, field, asdict
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable,
)

from app.services.tax_calculator import (
    PTKPStatus, calculate_pph21_annual, PTKP,
)

logger = logging.getLogger(__name__)


@dataclass
class BuktiPotongData:
    """Extracted data from a single bukti potong."""
    jenis: str = "1721-A1"
    npwp_pemotong: str = ""
    nama_pemotong: str = ""
    gaji: float = 0
    tunjangan_pph: float = 0
    tunjangan_lainnya: float = 0
    honorarium: float = 0
    premi_asuransi: float = 0
    natura: float = 0
    bonus_thr: float = 0
    total_bruto: float = 0
    biaya_jabatan: float = 0
    iuran_pensiun: float = 0
    neto: float = 0
    pph21_dipotong: float = 0
    nomor_bukti_potong: str = ""
    masa_pajak: str = "01-12"


@dataclass
class SPT1770SSData:
    """SPT 1770SS — for employees with single income source, bruto < 60M/year."""
    tahun_pajak: int = 2025
    npwp: str = ""
    nama: str = ""
    nik: str = ""
    alamat: str = ""
    pekerjaan: str = ""
    status_ptkp: str = "TK/0"

    # Income
    penghasilan_bruto: float = 0
    pengurang: float = 0
    penghasilan_neto: float = 0
    penghasilan_lainnya: float = 0  # Interest, dividends, etc.
    total_penghasilan: float = 0

    # Tax
    ptkp: float = 0
    pkp: float = 0
    pph_terutang: float = 0
    pph_dipotong: float = 0
    pph_kurang_bayar: float = 0
    pph_lebih_bayar: float = 0

    # Assets & Liabilities (simplified)
    total_harta: float = 0
    total_utang: float = 0

    # Source documents
    bukti_potong: list = field(default_factory=list)

    # Metadata
    status: str = "draft"  # draft, review, approved, filed


@dataclass
class SPT1770SData:
    """SPT 1770S — for employees with multiple income sources or bruto >= 60M."""
    tahun_pajak: int = 2025
    npwp: str = ""
    nama: str = ""
    nik: str = ""
    alamat: str = ""
    pekerjaan: str = ""
    status_ptkp: str = "TK/0"

    # Lampiran I — Employment income details
    penghasilan_neto_dalam_negeri: list = field(default_factory=list)  # Per employer
    penghasilan_neto_luar_negeri: float = 0
    penghasilan_lainnya: float = 0  # Bunga, dividen, sewa, royalti
    total_penghasilan_neto: float = 0

    # Deductions
    zakat: float = 0
    kompensasi_kerugian: float = 0

    # Calculation
    penghasilan_kena_pajak_setahun: float = 0
    ptkp: float = 0
    pkp: float = 0
    pph_terutang: float = 0

    # Credits
    pph_dipotong_pemberi_kerja: float = 0  # From 1721-A1/A2
    pph_dipotong_pihak_lain: float = 0  # PPh 22, 23, 24
    pph25_dibayar_sendiri: float = 0
    total_kredit_pajak: float = 0

    # Result
    pph_kurang_bayar: float = 0
    pph_lebih_bayar: float = 0
    pph25_angsuran_tahun_depan: float = 0

    # Assets
    total_harta: float = 0
    total_utang: float = 0

    bukti_potong: list = field(default_factory=list)
    status: str = "draft"


def generate_spt_1770ss(bukti_potong_list: list[BuktiPotongData], user_data: dict) -> SPT1770SSData:
    """Generate SPT 1770SS from bukti potong data."""
    total_bruto = sum(bp.total_bruto for bp in bukti_potong_list)
    total_pengurang = sum(bp.biaya_jabatan + bp.iuran_pensiun for bp in bukti_potong_list)
    total_neto = sum(bp.neto for bp in bukti_potong_list)
    total_pph_dipotong = sum(bp.pph21_dipotong for bp in bukti_potong_list)

    ptkp_status = PTKPStatus(user_data.get("status_ptkp", "TK/0"))
    ptkp_amount = PTKP[ptkp_status]

    result = calculate_pph21_annual(
        gross_income=total_bruto,
        ptkp_status=ptkp_status,
        iuran_pensiun=sum(bp.iuran_pensiun for bp in bukti_potong_list),
        tax_paid=total_pph_dipotong,
    )

    spt = SPT1770SSData(
        tahun_pajak=user_data.get("tahun_pajak", 2025),
        npwp=user_data.get("npwp", ""),
        nama=user_data.get("nama", ""),
        nik=user_data.get("nik", ""),
        alamat=user_data.get("alamat", ""),
        pekerjaan=user_data.get("pekerjaan", "Karyawan"),
        status_ptkp=ptkp_status.value,
        penghasilan_bruto=total_bruto,
        pengurang=total_pengurang,
        penghasilan_neto=total_neto,
        total_penghasilan=total_neto,
        ptkp=ptkp_amount,
        pkp=result.taxable_income,
        pph_terutang=result.tax_due,
        pph_dipotong=total_pph_dipotong,
        pph_kurang_bayar=result.tax_underpaid,
        pph_lebih_bayar=result.tax_overpaid,
        total_harta=user_data.get("total_harta", 0),
        total_utang=user_data.get("total_utang", 0),
        bukti_potong=[asdict(bp) for bp in bukti_potong_list],
        status="review",
    )
    return spt


def generate_spt_1770s(bukti_potong_list: list[BuktiPotongData], user_data: dict) -> SPT1770SData:
    """Generate SPT 1770S from multiple bukti potong."""
    ptkp_status = PTKPStatus(user_data.get("status_ptkp", "TK/0"))
    ptkp_amount = PTKP[ptkp_status]

    employer_incomes = []
    total_pph_dipotong = 0
    total_neto = 0

    for bp in bukti_potong_list:
        employer_incomes.append({
            "nama_pemotong": bp.nama_pemotong,
            "npwp_pemotong": bp.npwp_pemotong,
            "penghasilan_bruto": bp.total_bruto,
            "penghasilan_neto": bp.neto,
            "pph_dipotong": bp.pph21_dipotong,
        })
        total_pph_dipotong += bp.pph21_dipotong
        total_neto += bp.neto

    penghasilan_lainnya = user_data.get("penghasilan_lainnya", 0)
    zakat = user_data.get("zakat", 0)
    total_penghasilan = total_neto + penghasilan_lainnya
    pkp = max(0, total_penghasilan - zakat - ptkp_amount)

    result = calculate_pph21_annual(
        gross_income=sum(bp.total_bruto for bp in bukti_potong_list),
        ptkp_status=ptkp_status,
        iuran_pensiun=sum(bp.iuran_pensiun for bp in bukti_potong_list),
        tax_paid=total_pph_dipotong,
    )

    pph25_angsuran = max(0, result.tax_due / 12) if result.tax_underpaid > 0 else 0

    spt = SPT1770SData(
        tahun_pajak=user_data.get("tahun_pajak", 2025),
        npwp=user_data.get("npwp", ""),
        nama=user_data.get("nama", ""),
        nik=user_data.get("nik", ""),
        alamat=user_data.get("alamat", ""),
        pekerjaan=user_data.get("pekerjaan", "Karyawan"),
        status_ptkp=ptkp_status.value,
        penghasilan_neto_dalam_negeri=employer_incomes,
        penghasilan_lainnya=penghasilan_lainnya,
        total_penghasilan_neto=total_penghasilan,
        zakat=zakat,
        penghasilan_kena_pajak_setahun=total_penghasilan - zakat,
        ptkp=ptkp_amount,
        pkp=pkp,
        pph_terutang=result.tax_due,
        pph_dipotong_pemberi_kerja=total_pph_dipotong,
        total_kredit_pajak=total_pph_dipotong,
        pph_kurang_bayar=result.tax_underpaid,
        pph_lebih_bayar=result.tax_overpaid,
        pph25_angsuran_tahun_depan=pph25_angsuran,
        total_harta=user_data.get("total_harta", 0),
        total_utang=user_data.get("total_utang", 0),
        bukti_potong=[asdict(bp) for bp in bukti_potong_list],
        status="review",
    )
    return spt


def _fmt(n: float) -> str:
    return f"Rp {n:,.0f}".replace(",", ".")


def generate_spt_pdf(spt_data: SPT1770SSData | SPT1770SData) -> bytes:
    """Generate a PDF summary of the SPT for review before filing."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    # Title style
    title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=16,
                                  textColor=colors.HexColor("#1a56db"), spaceAfter=4 * mm)
    subtitle_style = ParagraphStyle("subtitle", parent=styles["Normal"], fontSize=9,
                                     textColor=colors.HexColor("#475569"), spaceAfter=8 * mm)
    section_style = ParagraphStyle("section", parent=styles["Heading2"], fontSize=12,
                                    textColor=colors.HexColor("#0f172a"), spaceBefore=6 * mm, spaceAfter=3 * mm)

    is_1770ss = isinstance(spt_data, SPT1770SSData)
    form_type = "1770 SS" if is_1770ss else "1770 S"

    # Header
    story.append(Paragraph(f"SPT Tahunan PPh Orang Pribadi — {form_type}", title_style))
    story.append(Paragraph(
        f"Tahun Pajak {spt_data.tahun_pajak} | Dibuat oleh Pajakia | Status: {spt_data.status.upper()}",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 4 * mm))

    # Identity
    story.append(Paragraph("A. Identitas Wajib Pajak", section_style))
    identity_data = [
        ["NPWP", spt_data.npwp or "—"],
        ["Nama", spt_data.nama or "—"],
        ["NIK", spt_data.nik or "—"],
        ["Alamat", spt_data.alamat or "—"],
        ["Pekerjaan", spt_data.pekerjaan or "—"],
        ["Status PTKP", spt_data.status_ptkp],
    ]
    t = Table(identity_data, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
    ]))
    story.append(t)

    # Income
    story.append(Paragraph("B. Penghasilan", section_style))
    if is_1770ss:
        income_data = [
            ["Penghasilan Bruto", _fmt(spt_data.penghasilan_bruto)],
            ["Pengurang (Biaya Jabatan + Iuran)", _fmt(spt_data.pengurang)],
            ["Penghasilan Neto", _fmt(spt_data.penghasilan_neto)],
        ]
    else:
        income_data = [
            ["Total Penghasilan Neto", _fmt(spt_data.total_penghasilan_neto)],
            ["Penghasilan Lainnya", _fmt(spt_data.penghasilan_lainnya)],
            ["Zakat/Sumbangan Keagamaan", _fmt(spt_data.zakat)],
        ]
        # Per-employer breakdown
        for i, emp in enumerate(spt_data.penghasilan_neto_dalam_negeri):
            income_data.insert(i, [
                f"  {emp.get('nama_pemotong', f'Pemberi Kerja {i+1}')}",
                _fmt(emp.get("penghasilan_neto", 0)),
            ])

    t = Table(income_data, colWidths=[10 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]))
    story.append(t)

    # Tax calculation
    story.append(Paragraph("C. Perhitungan PPh 21", section_style))
    tax_data = [
        ["PTKP", _fmt(spt_data.ptkp)],
        ["Penghasilan Kena Pajak (PKP)", _fmt(spt_data.pkp)],
        ["PPh 21 Terutang", _fmt(spt_data.pph_terutang)],
        ["PPh 21 Telah Dipotong", _fmt(spt_data.pph_dipotong if is_1770ss else spt_data.pph_dipotong_pemberi_kerja)],
    ]

    kurang_bayar = spt_data.pph_kurang_bayar
    lebih_bayar = spt_data.pph_lebih_bayar
    if kurang_bayar > 0:
        tax_data.append(["PPh Kurang Bayar", _fmt(kurang_bayar)])
    elif lebih_bayar > 0:
        tax_data.append(["PPh Lebih Bayar (Restitusi)", _fmt(lebih_bayar)])
    else:
        tax_data.append(["Status", "NIHIL"])

    t = Table(tax_data, colWidths=[10 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1a56db")),
    ]))
    story.append(t)

    # Assets summary
    story.append(Paragraph("D. Harta dan Kewajiban", section_style))
    assets_data = [
        ["Total Harta", _fmt(spt_data.total_harta)],
        ["Total Utang", _fmt(spt_data.total_utang)],
    ]
    t = Table(assets_data, colWidths=[10 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]))
    story.append(t)

    # Bukti potong list
    if spt_data.bukti_potong:
        story.append(Paragraph("E. Daftar Bukti Potong", section_style))
        bp_header = ["No", "Pemotong", "No. Bukti Potong", "Bruto", "PPh Dipotong"]
        bp_rows = [bp_header]
        for i, bp in enumerate(spt_data.bukti_potong):
            bp_rows.append([
                str(i + 1),
                bp.get("nama_pemotong", "—"),
                bp.get("nomor_bukti_potong", "—"),
                _fmt(bp.get("total_bruto", 0)),
                _fmt(bp.get("pph21_dipotong", 0)),
            ])
        t = Table(bp_rows, colWidths=[1 * cm, 5 * cm, 4 * cm, 3.5 * cm, 3.5 * cm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (3, 0), (4, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ]))
        story.append(t)

    # Footer
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0")))
    footer_style = ParagraphStyle("footer", parent=styles["Normal"], fontSize=8,
                                   textColor=colors.HexColor("#94a3b8"), alignment=1)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Dokumen ini dibuat dengan Pajakia — pajakia.com", footer_style))
    story.append(Paragraph(
        "Dokumen ini bukan SPT resmi. Gunakan data ini untuk mengisi SPT di Coretax/DJP Online.",
        footer_style,
    ))

    doc.build(story)
    return buf.getvalue()
