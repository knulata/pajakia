"""Tax calculation API endpoints."""

from dataclasses import asdict
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tax_calculator import (
    PTKPStatus,
    calculate_pph21_annual,
    calculate_pph21_monthly_ter,
    PTKP,
)

router = APIRouter(prefix="/tax", tags=["tax"])


class PPh21AnnualRequest(BaseModel):
    gross_income: float
    ptkp_status: str = "TK/0"
    iuran_pensiun: float = 0
    tax_paid: float = 0


class PPh21MonthlyRequest(BaseModel):
    monthly_gross: float
    ptkp_status: str = "TK/0"


@router.post("/pph21/annual")
async def calc_pph21_annual(data: PPh21AnnualRequest):
    """Calculate annual PPh 21 (for SPT Tahunan)."""
    status = PTKPStatus(data.ptkp_status)
    result = calculate_pph21_annual(
        gross_income=data.gross_income,
        ptkp_status=status,
        iuran_pensiun=data.iuran_pensiun,
        tax_paid=data.tax_paid,
    )
    return asdict(result)


@router.post("/pph21/monthly")
async def calc_pph21_monthly(data: PPh21MonthlyRequest):
    """Calculate monthly PPh 21 using TER method."""
    status = PTKPStatus(data.ptkp_status)
    return calculate_pph21_monthly_ter(
        monthly_gross=data.monthly_gross,
        ptkp_status=status,
    )


@router.get("/ptkp")
async def get_ptkp_options():
    """Get all PTKP status options with amounts."""
    return [
        {"status": k.value, "amount": v, "label": _ptkp_label(k)}
        for k, v in PTKP.items()
    ]


def _ptkp_label(status: PTKPStatus) -> str:
    labels = {
        PTKPStatus.TK0: "Tidak Kawin, tanpa tanggungan",
        PTKPStatus.TK1: "Tidak Kawin, 1 tanggungan",
        PTKPStatus.TK2: "Tidak Kawin, 2 tanggungan",
        PTKPStatus.TK3: "Tidak Kawin, 3 tanggungan",
        PTKPStatus.K0: "Kawin, tanpa tanggungan",
        PTKPStatus.K1: "Kawin, 1 tanggungan",
        PTKPStatus.K2: "Kawin, 2 tanggungan",
        PTKPStatus.K3: "Kawin, 3 tanggungan",
        PTKPStatus.KI0: "Kawin, penghasilan istri digabung, tanpa tanggungan",
        PTKPStatus.KI1: "Kawin, penghasilan istri digabung, 1 tanggungan",
        PTKPStatus.KI2: "Kawin, penghasilan istri digabung, 2 tanggungan",
        PTKPStatus.KI3: "Kawin, penghasilan istri digabung, 3 tanggungan",
    }
    return labels.get(status, status.value)
