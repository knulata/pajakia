"""Consultant dashboard API — client management, batch processing, deadlines."""

from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.client import Client, ClientStatus, EntityType
from app.services.tax_calendar import ObligationType, get_client_deadlines, DeadlineStatus
from app.services.batch_processor import process_batch_ocr, batch_generate_spt
from app.services.nudge_engine import send_document_request

router = APIRouter(prefix="/consultant", tags=["consultant"])


def _require_consultant(user: User):
    if user.role not in (UserRole.CONSULTANT, UserRole.ADMIN):
        raise HTTPException(403, "Consultant access required")


# --- Client Management ---

class ClientCreate(BaseModel):
    name: str
    npwp: str | None = None
    nik: str | None = None
    email: str | None = None
    phone: str | None = None
    entity_type: str = "orang_pribadi"
    is_pkp: bool = False
    ptkp_status: str | None = None
    tax_obligations: list[str] | None = None
    fee_monthly: float | None = None
    notes: str | None = None


class ClientOut(BaseModel):
    id: str
    name: str
    npwp: str | None
    phone: str | None
    entity_type: str
    status: str
    is_pkp: bool
    ptkp_status: str | None
    tax_obligations: list | None
    fee_monthly: float | None

    model_config = {"from_attributes": True}


@router.get("/clients", response_model=list[ClientOut])
async def list_clients(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_consultant(user)
    result = await db.execute(
        select(Client).where(Client.consultant_id == user.id).order_by(Client.name)
    )
    return [_client_out(c) for c in result.scalars().all()]


@router.post("/clients", response_model=ClientOut)
async def create_client(
    data: ClientCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_consultant(user)
    client = Client(
        consultant_id=user.id,
        name=data.name,
        npwp=data.npwp,
        nik=data.nik,
        email=data.email,
        phone=data.phone,
        entity_type=EntityType(data.entity_type),
        is_pkp=data.is_pkp,
        ptkp_status=data.ptkp_status,
        tax_obligations=data.tax_obligations,
        fee_monthly=data.fee_monthly,
        notes=data.notes,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return _client_out(client)


@router.get("/clients/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_consultant(user)
    client = await _get_consultant_client(client_id, user.id, db)
    return _client_out(client)


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_consultant(user)
    client = await _get_consultant_client(client_id, user.id, db)
    client.status = ClientStatus.INACTIVE
    await db.commit()
    return {"status": "deactivated"}


# --- Deadlines ---

@router.get("/deadlines")
async def get_all_deadlines(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming deadlines across all clients."""
    _require_consultant(user)
    result = await db.execute(
        select(Client).where(
            Client.consultant_id == user.id,
            Client.status == ClientStatus.ACTIVE,
        )
    )
    clients = result.scalars().all()

    all_deadlines = []
    for client in clients:
        obligations = [
            ObligationType(o) for o in (client.tax_obligations or [])
            if o in [e.value for e in ObligationType]
        ]
        if not obligations:
            continue

        deadlines = get_client_deadlines(obligations=obligations, months_ahead=2)
        for dl in deadlines:
            all_deadlines.append({
                "client_id": client.id,
                "client_name": client.name,
                "obligation": dl.obligation.value,
                "label": dl.label,
                "deadline_date": str(dl.deadline_date),
                "payment_deadline": str(dl.payment_deadline),
                "status": dl.status.value,
                "days_remaining": dl.days_remaining,
                "penalty_amount": dl.penalty_amount,
            })

    all_deadlines.sort(key=lambda d: d["deadline_date"])
    return {
        "total_clients": len(clients),
        "total_deadlines": len(all_deadlines),
        "overdue": sum(1 for d in all_deadlines if d["status"] == "overdue"),
        "due_soon": sum(1 for d in all_deadlines if d["status"] == "due_soon"),
        "deadlines": all_deadlines,
    }


# --- Batch Processing ---

class BatchOCRRequest(BaseModel):
    documents: list[dict]  # [{id, file_url, doc_type, mime_type}]


@router.post("/batch/ocr")
async def batch_ocr(
    data: BatchOCRRequest,
    user: User = Depends(get_current_user),
):
    """Process multiple documents through OCR in parallel."""
    _require_consultant(user)
    result = await process_batch_ocr(data.documents)
    return asdict(result)


class BatchSPTRequest(BaseModel):
    clients: list[dict]  # [{client_id, bukti_potong_extractions, user_data}]


@router.post("/batch/spt")
async def batch_spt(
    data: BatchSPTRequest,
    user: User = Depends(get_current_user),
):
    """Generate SPT for multiple clients in parallel."""
    _require_consultant(user)
    results = await batch_generate_spt(data.clients)
    return {"results": results}


# --- Document Requests ---

class DocRequestPayload(BaseModel):
    client_id: str
    doc_types: list[str]
    masa: int
    tahun: int


@router.post("/request-documents")
async def request_documents(
    data: DocRequestPayload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send document collection request to client via WhatsApp."""
    _require_consultant(user)
    client = await _get_consultant_client(data.client_id, user.id, db)
    phone = client.whatsapp_id or client.phone
    if not phone:
        raise HTTPException(400, "Client has no WhatsApp number")

    result = await send_document_request(
        phone=phone,
        client_name=client.name,
        doc_types=data.doc_types,
        masa=data.masa,
        tahun=data.tahun,
    )
    return result


# --- Analytics ---

@router.get("/analytics")
async def get_analytics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard analytics for consultant."""
    _require_consultant(user)
    result = await db.execute(
        select(Client).where(Client.consultant_id == user.id)
    )
    clients = result.scalars().all()

    active = [c for c in clients if c.status == ClientStatus.ACTIVE]
    total_revenue = sum(c.fee_monthly or 0 for c in active)

    entity_breakdown = {}
    for c in active:
        et = c.entity_type.value
        entity_breakdown[et] = entity_breakdown.get(et, 0) + 1

    return {
        "total_clients": len(clients),
        "active_clients": len(active),
        "monthly_revenue": total_revenue,
        "annual_revenue_projection": total_revenue * 12,
        "entity_breakdown": entity_breakdown,
        "pkp_clients": sum(1 for c in active if c.is_pkp),
        "non_pkp_clients": sum(1 for c in active if not c.is_pkp),
    }


# --- Helpers ---

async def _get_consultant_client(client_id: str, consultant_id: str, db: AsyncSession) -> Client:
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.consultant_id == consultant_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(404, "Client not found")
    return client


def _client_out(c: Client) -> ClientOut:
    return ClientOut(
        id=c.id,
        name=c.name,
        npwp=c.npwp,
        phone=c.phone,
        entity_type=c.entity_type.value,
        status=c.status.value,
        is_pkp=c.is_pkp,
        ptkp_status=c.ptkp_status,
        tax_obligations=c.tax_obligations,
        fee_monthly=c.fee_monthly,
    )
