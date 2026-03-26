"""Tax filing CRUD endpoints with pagination and filtering."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tax_filing import TaxFiling, FilingType, FilingStatus
from app.models.document import Document

router = APIRouter(prefix="/filings", tags=["filings"])


class FilingCreate(BaseModel):
    filing_type: FilingType
    tax_year: int
    tax_month: int | None = None


class FilingOut(BaseModel):
    id: str
    filing_type: str
    status: str
    tax_year: int
    tax_month: int | None
    gross_income: float | None
    tax_due: float | None
    tax_underpaid: float | None
    deadline: str | None
    filed_at: str | None
    created_at: str
    model_config = {"from_attributes": True}


@router.post("/", response_model=FilingOut)
async def create_filing(data: FilingCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    filing = TaxFiling(user_id=user.id, filing_type=data.filing_type, tax_year=data.tax_year, tax_month=data.tax_month)
    db.add(filing)
    await db.commit()
    await db.refresh(filing)
    return _to_out(filing)


@router.get("/")
async def list_filings(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    tax_year: int | None = Query(None), status: str = Query(""),
    filing_type: str = Query(""),
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    query = select(TaxFiling).where(TaxFiling.user_id == user.id)
    if tax_year:
        query = query.where(TaxFiling.tax_year == tax_year)
    if status:
        query = query.where(TaxFiling.status == FilingStatus(status))
    if filing_type:
        query = query.where(TaxFiling.filing_type == FilingType(filing_type))
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(TaxFiling.created_at.desc()).offset(offset).limit(page_size))
    filings = result.scalars().all()
    return {"items": [_to_out(f) for f in filings], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}


@router.get("/{filing_id}", response_model=FilingOut)
async def get_filing(filing_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    filing = await _get_user_filing(filing_id, user.id, db)
    return _to_out(filing)


@router.get("/{filing_id}/documents")
async def get_filing_documents(filing_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _get_user_filing(filing_id, user.id, db)
    result = await db.execute(select(Document).where(Document.filing_id == filing_id))
    docs = result.scalars().all()
    return [{"id": d.id, "doc_type": d.doc_type.value, "status": d.status.value, "file_name": d.file_name, "ocr_confidence": d.ocr_confidence, "created_at": str(d.created_at)} for d in docs]


@router.get("/{filing_id}/year-comparison")
async def year_over_year(filing_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current = await _get_user_filing(filing_id, user.id, db)
    prev_result = await db.execute(select(TaxFiling).where(TaxFiling.user_id == user.id, TaxFiling.filing_type == current.filing_type, TaxFiling.tax_year == current.tax_year - 1, TaxFiling.tax_month == current.tax_month))
    prev = prev_result.scalar_one_or_none()
    def _sf(v): return float(v) if v else 0
    current_data = {"tax_year": current.tax_year, "gross_income": _sf(current.gross_income), "tax_due": _sf(current.tax_due), "deductions": _sf(current.deductions)}
    if prev:
        prev_data = {"tax_year": prev.tax_year, "gross_income": _sf(prev.gross_income), "tax_due": _sf(prev.tax_due), "deductions": _sf(prev.deductions)}
        changes = {}
        for key in ("gross_income", "tax_due", "deductions"):
            old, new = prev_data[key], current_data[key]
            changes[key] = {"absolute": new - old, "percentage": round(((new - old) / old) * 100, 1) if old else None}
    else:
        prev_data, changes = None, None
    return {"current": current_data, "previous": prev_data, "changes": changes}


async def _get_user_filing(filing_id: str, user_id: str, db: AsyncSession) -> TaxFiling:
    result = await db.execute(select(TaxFiling).where(TaxFiling.id == filing_id, TaxFiling.user_id == user_id))
    filing = result.scalar_one_or_none()
    if not filing:
        raise HTTPException(status_code=404, detail="Filing not found")
    return filing


def _to_out(filing: TaxFiling) -> FilingOut:
    return FilingOut(
        id=filing.id, filing_type=filing.filing_type.value, status=filing.status.value,
        tax_year=filing.tax_year, tax_month=filing.tax_month,
        gross_income=float(filing.gross_income) if filing.gross_income else None,
        tax_due=float(filing.tax_due) if filing.tax_due else None,
        tax_underpaid=float(filing.tax_underpaid) if filing.tax_underpaid else None,
        deadline=str(filing.deadline) if filing.deadline else None,
        filed_at=str(filing.filed_at) if filing.filed_at else None,
        created_at=str(filing.created_at),
    )
