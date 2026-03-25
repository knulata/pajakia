"""SPT generation and PDF download endpoints."""

from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.spt_generator import (
    BuktiPotongData, generate_spt_1770ss, generate_spt_1770s, generate_spt_pdf,
    SPT1770SSData, SPT1770SData,
)
from app.services.spt_masa_pph21 import (
    Employee, generate_spt_masa_pph21, generate_ebupot_csv,
)
from app.services.efaktur import (
    invoices_to_fakturs, generate_efaktur_csv, calculate_ppn_summary,
    FakturPajakItem,
)

router = APIRouter(prefix="/spt", tags=["spt"])


class SPTRequest(BaseModel):
    bukti_potong: list[dict]
    user_data: dict


@router.post("/generate/1770ss")
async def generate_1770ss(data: SPTRequest, user: User = Depends(get_current_user)):
    """Generate SPT 1770SS from bukti potong data."""
    bp_list = [BuktiPotongData(**bp) for bp in data.bukti_potong]
    spt = generate_spt_1770ss(bp_list, data.user_data)
    return asdict(spt)


@router.post("/generate/1770s")
async def generate_1770s(data: SPTRequest, user: User = Depends(get_current_user)):
    """Generate SPT 1770S from bukti potong data."""
    bp_list = [BuktiPotongData(**bp) for bp in data.bukti_potong]
    spt = generate_spt_1770s(bp_list, data.user_data)
    return asdict(spt)


@router.post("/pdf/1770ss")
async def download_1770ss_pdf(data: SPTRequest, user: User = Depends(get_current_user)):
    """Generate and download SPT 1770SS as PDF."""
    bp_list = [BuktiPotongData(**bp) for bp in data.bukti_potong]
    spt = generate_spt_1770ss(bp_list, data.user_data)
    pdf_bytes = generate_spt_pdf(spt)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SPT_1770SS_{spt.tahun_pajak}.pdf"},
    )


@router.post("/pdf/1770s")
async def download_1770s_pdf(data: SPTRequest, user: User = Depends(get_current_user)):
    """Generate and download SPT 1770S as PDF."""
    bp_list = [BuktiPotongData(**bp) for bp in data.bukti_potong]
    spt = generate_spt_1770s(bp_list, data.user_data)
    pdf_bytes = generate_spt_pdf(spt)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SPT_1770S_{spt.tahun_pajak}.pdf"},
    )


# --- SPT Masa PPh 21 ---

class MasaPPh21Request(BaseModel):
    employees: list[dict]
    masa: int
    tahun: int
    pemotong_npwp: str = ""
    pemotong_nama: str = ""
    cumulative_data: dict | None = None


@router.post("/masa/pph21")
async def generate_masa_pph21(data: MasaPPh21Request, user: User = Depends(get_current_user)):
    """Generate SPT Masa PPh 21."""
    emps = [Employee(**e) for e in data.employees]
    spt = generate_spt_masa_pph21(
        employees=emps,
        masa=data.masa,
        tahun=data.tahun,
        pemotong_npwp=data.pemotong_npwp,
        pemotong_nama=data.pemotong_nama,
        cumulative_data=data.cumulative_data,
    )
    return asdict(spt)


@router.post("/masa/pph21/ebupot-csv")
async def download_ebupot_csv(data: MasaPPh21Request, user: User = Depends(get_current_user)):
    """Generate e-Bupot CSV for Coretax upload."""
    emps = [Employee(**e) for e in data.employees]
    spt = generate_spt_masa_pph21(
        employees=emps,
        masa=data.masa,
        tahun=data.tahun,
        pemotong_npwp=data.pemotong_npwp,
        pemotong_nama=data.pemotong_nama,
    )
    csv_content = generate_ebupot_csv(spt)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ebupot_pph21_{data.masa:02d}_{data.tahun}.csv"},
    )


# --- e-Faktur / PPN ---

class EFakturRequest(BaseModel):
    invoices: list[dict]
    seller_npwp: str
    ppn_rate: float = 0.11


@router.post("/efaktur/generate")
async def generate_efaktur(data: EFakturRequest, user: User = Depends(get_current_user)):
    """Generate e-Faktur entries from invoices."""
    fakturs = invoices_to_fakturs(data.invoices, data.seller_npwp, data.ppn_rate)
    return {"fakturs": [f.__dict__ for f in fakturs]}


@router.post("/efaktur/csv")
async def download_efaktur_csv(data: EFakturRequest, user: User = Depends(get_current_user)):
    """Generate e-Faktur CSV for DJP import."""
    fakturs = invoices_to_fakturs(data.invoices, data.seller_npwp, data.ppn_rate)
    csv_content = generate_efaktur_csv(fakturs)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=efaktur_import.csv"},
    )


class PPNSummaryRequest(BaseModel):
    faktur_keluaran: list[dict]
    faktur_masukan: list[dict]
    masa: int
    tahun: int


@router.post("/ppn/summary")
async def ppn_summary(data: PPNSummaryRequest, user: User = Depends(get_current_user)):
    """Calculate monthly PPN summary."""
    keluaran = [FakturPajakItem(**f) for f in data.faktur_keluaran]
    masukan = [FakturPajakItem(**f) for f in data.faktur_masukan]
    summary = calculate_ppn_summary(keluaran, masukan, data.masa, data.tahun)
    return summary.__dict__
