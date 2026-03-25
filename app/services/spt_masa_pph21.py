"""SPT Masa PPh 21 generator — monthly employee withholding tax."""

import io
import logging
from dataclasses import dataclass, field, asdict
from datetime import date

from app.services.tax_calculator import PTKPStatus, calculate_pph21_monthly_ter, calculate_pph21_december

logger = logging.getLogger(__name__)


@dataclass
class Employee:
    nama: str
    npwp: str = ""
    nik: str = ""
    status_ptkp: str = "TK/0"
    gaji_pokok: float = 0
    tunjangan: float = 0
    bonus: float = 0  # Only in specific months (THR, etc.)
    premi_asuransi: float = 0
    iuran_pensiun: float = 0


@dataclass
class EmployeePPh21:
    nama: str
    npwp: str
    penghasilan_bruto: float
    ter_rate: float
    pph21: float
    ter_category: str


@dataclass
class SPTMasaPPh21:
    masa: int  # 1-12
    tahun: int
    npwp_pemotong: str = ""
    nama_pemotong: str = ""

    # Summary
    jumlah_pegawai: int = 0
    total_bruto: float = 0
    total_pph21: float = 0

    # Detail per employee
    detail_pegawai: list = field(default_factory=list)

    # For December true-up
    is_december: bool = False
    total_ter_jan_nov: float = 0
    annual_true_up: float = 0


def generate_spt_masa_pph21(
    employees: list[Employee],
    masa: int,
    tahun: int,
    pemotong_npwp: str = "",
    pemotong_nama: str = "",
    cumulative_data: dict | None = None,
) -> SPTMasaPPh21:
    """Generate monthly SPT Masa PPh 21 for all employees.

    For Jan-Nov: uses TER method
    For December: uses progressive rate true-up
    """
    is_december = masa == 12
    detail = []
    total_bruto = 0
    total_pph = 0

    for emp in employees:
        monthly_bruto = emp.gaji_pokok + emp.tunjangan + emp.bonus + emp.premi_asuransi

        if is_december and cumulative_data:
            # December true-up: annual progressive rate - TER paid Jan-Nov
            emp_cumulative = cumulative_data.get(emp.npwp or emp.nik, {})
            annual_bruto = emp_cumulative.get("annual_bruto", 0) + monthly_bruto
            total_ter_paid = emp_cumulative.get("total_ter_paid", 0)

            try:
                ptkp = PTKPStatus(emp.status_ptkp)
            except ValueError:
                ptkp = PTKPStatus.TK0

            dec_result = calculate_pph21_december(
                annual_gross=annual_bruto,
                ptkp_status=ptkp,
                total_ter_paid_jan_nov=total_ter_paid,
                iuran_pensiun=emp.iuran_pensiun * 12,
            )

            pph21 = dec_result["december_tax"]
            detail.append(EmployeePPh21(
                nama=emp.nama,
                npwp=emp.npwp,
                penghasilan_bruto=monthly_bruto,
                ter_rate=0,
                pph21=pph21,
                ter_category="DEC",
            ))
        else:
            # Jan-Nov: TER method
            try:
                ptkp = PTKPStatus(emp.status_ptkp)
            except ValueError:
                ptkp = PTKPStatus.TK0

            result = calculate_pph21_monthly_ter(
                monthly_gross=monthly_bruto,
                ptkp_status=ptkp,
            )
            pph21 = result["monthly_tax"]
            detail.append(EmployeePPh21(
                nama=emp.nama,
                npwp=emp.npwp,
                penghasilan_bruto=monthly_bruto,
                ter_rate=result["ter_rate"],
                pph21=pph21,
                ter_category=result["ter_category"],
            ))

        total_bruto += monthly_bruto
        total_pph += pph21

    return SPTMasaPPh21(
        masa=masa,
        tahun=tahun,
        npwp_pemotong=pemotong_npwp,
        nama_pemotong=pemotong_nama,
        jumlah_pegawai=len(employees),
        total_bruto=total_bruto,
        total_pph21=total_pph,
        detail_pegawai=[asdict(d) for d in detail],
        is_december=is_december,
    )


def generate_ebupot_csv(spt: SPTMasaPPh21) -> str:
    """Generate e-Bupot CSV for upload to Coretax/DJP."""
    output = io.StringIO()
    import csv
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "No", "NPWP", "Nama", "Kode Objek Pajak",
        "Penghasilan Bruto", "PPh Dipotong",
        "Masa Pajak", "Tahun Pajak",
    ])

    for i, emp in enumerate(spt.detail_pegawai, 1):
        writer.writerow([
            i,
            emp.get("npwp", ""),
            emp.get("nama", ""),
            "21-100-01",  # Pegawai tetap
            int(emp.get("penghasilan_bruto", 0)),
            int(emp.get("pph21", 0)),
            f"{spt.masa:02d}",
            spt.tahun,
        ])

    return output.getvalue()
