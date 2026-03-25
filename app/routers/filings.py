"""Tax filing CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    created_at: str

    model_config = {"from_attributes": True}


@router.post("/", response_model=FilingOut)
async def create_filing(
    data: FilingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tax filing."""
    filing = TaxFiling(
        user_id=user.id,
        filing_type=data.filing_type,
        tax_year=data.tax_year,
        tax_month=data.tax_month,
    )
    db.add(filing)
    await db.commit()
    await db.refresh(filing)
    return _to_out(filing)


@router.get("/", response_model=list[FilingOut])
async def list_filings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all filings for the current user."""
    result = await db.execute(
        select(TaxFiling)
        .where(TaxFiling.user_id == user.id)
        .order_by(TaxFiling.created_at.desc())
    )
    filings = result.scalars().all()
    return [_to_out(f) for f in filings]


@router.get("/{filing_id}", response_model=FilingOut)
async def get_filing(
    filing_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific filing."""
    filing = await _get_user_filing(filing_id, user.id, db)
    return _to_out(filing)


@router.get("/{filing_id}/documents")
async def get_filing_documents(
    filing_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List documents attached to a filing."""
    await _get_user_filing(filing_id, user.id, db)
    result = await db.execute(
        select(Document).where(Document.filing_id == filing_id)
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "doc_type": d.doc_type.value,
            "status": d.status.value,
            "file_name": d.file_name,
            "ocr_confidence": d.ocr_confidence,
            "created_at": str(d.created_at),
        }
        for d in docs
    ]


async def _get_user_filing(
    filing_id: str, user_id: str, db: AsyncSession
) -> TaxFiling:
    result = await db.execute(
        select(TaxFiling).where(
            TaxFiling.id == filing_id, TaxFiling.user_id == user_id
        )
    )
    filing = result.scalar_one_or_none()
    if not filing:
        raise HTTPException(status_code=404, detail="Filing not found")
    return filing


def _to_out(filing: TaxFiling) -> FilingOut:
    return FilingOut(
        id=filing.id,
        filing_type=filing.filing_type.value,
        status=filing.status.value,
        tax_year=filing.tax_year,
        tax_month=filing.tax_month,
        gross_income=float(filing.gross_income) if filing.gross_income else None,
        tax_due=float(filing.tax_due) if filing.tax_due else None,
        tax_underpaid=float(filing.tax_underpaid) if filing.tax_underpaid else None,
        created_at=str(filing.created_at),
    )
