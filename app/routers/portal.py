"""Client self-service portal — token-based document upload without login."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.file_validation import validate_upload
from app.models.portal_token import PortalToken
from app.models.client import Client
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.consent import ClientConsent, ConsentType, ConsentStatus
from app.models.audit_log import AuditLog
from app.services.document_store import store_document

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portal", tags=["portal"])


async def _get_portal_context(token: str, db: AsyncSession):
    result = await db.execute(
        select(PortalToken).where(PortalToken.token == token)
    )
    portal = result.scalar_one_or_none()
    if not portal:
        raise HTTPException(404, "Invalid portal link")
    if not portal.is_active:
        raise HTTPException(410, "This portal link has been deactivated")
    if portal.expires_at < datetime.now(timezone.utc):
        raise HTTPException(410, "This portal link has expired")
    portal.last_accessed = datetime.now(timezone.utc)
    client_result = await db.execute(select(Client).where(Client.id == portal.client_id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(404, "Client not found")
    return portal, client


@router.get("/{token}")
async def get_portal_info(token: str, db: AsyncSession = Depends(get_db)):
    portal, client = await _get_portal_context(token, db)
    uploaded_docs = []
    if client.user_id:
        doc_result = await db.execute(
            select(Document).where(Document.user_id == client.user_id).order_by(Document.created_at.desc())
        )
        for d in doc_result.scalars().all():
            uploaded_docs.append({
                "id": d.id, "doc_type": d.doc_type.value, "file_name": d.file_name,
                "status": d.status.value, "created_at": str(d.created_at),
            })
    required = portal.required_documents or []
    uploaded_types = {d["doc_type"] for d in uploaded_docs}
    checklist = [{"doc_type": dt, "label": _doc_type_label(dt), "uploaded": dt in uploaded_types} for dt in required]
    consent_result = await db.execute(
        select(ClientConsent).where(ClientConsent.client_id == client.id, ClientConsent.status == ConsentStatus.GRANTED)
    )
    consents = [c.consent_type.value for c in consent_result.scalars().all()]
    await db.commit()
    return {
        "client_name": client.name, "tax_year": portal.tax_year, "tax_month": portal.tax_month,
        "checklist": checklist, "uploaded_documents": uploaded_docs, "consents_granted": consents,
        "expires_at": str(portal.expires_at),
    }


@router.post("/{token}/upload")
async def portal_upload_document(
    token: str, file: UploadFile = File(...), doc_type: str = Form("other"),
    tax_year: int | None = Form(None), tax_month: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    portal, client = await _get_portal_context(token, db)
    content = await validate_upload(file)
    if not client.user_id:
        from app.models.user import User
        shadow_user = User(email=client.email or f"portal-{client.id}@pajakia.internal", name=client.name, phone=client.phone)
        db.add(shadow_user)
        await db.flush()
        client.user_id = shadow_user.id
    file_url = await store_document(content=content, filename=file.filename or "upload", user_id=client.user_id, mime_type=file.content_type or "application/octet-stream")
    doc = Document(
        user_id=client.user_id,
        doc_type=DocumentType(doc_type) if doc_type in [e.value for e in DocumentType] else DocumentType.OTHER,
        status=DocumentStatus.UPLOADED, file_url=file_url, file_name=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream", file_size=len(content),
        tax_year=tax_year or portal.tax_year, tax_month=tax_month or portal.tax_month,
    )
    db.add(doc)
    db.add(AuditLog(user_id=client.user_id, action="portal_upload", resource_type="document", resource_id=doc.id, detail=f"Client self-service upload: {file.filename}"))
    await db.commit()
    await db.refresh(doc)
    return {"document_id": doc.id, "file_name": doc.file_name, "doc_type": doc.doc_type.value, "status": doc.status.value, "message": "Document uploaded successfully."}


@router.post("/{token}/consent")
async def grant_consent(token: str, consent_types: list[str] = Query(...), db: AsyncSession = Depends(get_db)):
    portal, client = await _get_portal_context(token, db)
    granted = []
    for ct in consent_types:
        try:
            consent_type = ConsentType(ct)
        except ValueError:
            continue
        existing = await db.execute(
            select(ClientConsent).where(ClientConsent.client_id == client.id, ClientConsent.consultant_id == portal.consultant_id, ClientConsent.consent_type == consent_type, ClientConsent.status == ConsentStatus.GRANTED)
        )
        if existing.scalar_one_or_none():
            granted.append(ct)
            continue
        consent = ClientConsent(client_id=client.id, consultant_id=portal.consultant_id, consent_type=consent_type, evidence=f"Granted via self-service portal token={portal.token[:8]}...")
        db.add(consent)
        granted.append(ct)
    db.add(AuditLog(action="grant_consent", resource_type="client", resource_id=client.id, detail=f"Consents granted: {granted}"))
    await db.commit()
    return {"granted": granted, "message": "Thank you for granting consent."}


def _doc_type_label(doc_type: str) -> str:
    labels = {
        "bukti_potong_1721_a1": "Bukti Potong 1721-A1 (Karyawan Swasta)",
        "bukti_potong_1721_a2": "Bukti Potong 1721-A2 (PNS/TNI/Polri)",
        "faktur_pajak": "Faktur Pajak",
        "bukti_potong_pph23": "Bukti Potong PPh 23",
        "bukti_potong_pph26": "Bukti Potong PPh 26",
        "bukti_potong_pph4_2": "Bukti Potong PPh 4(2)",
        "invoice": "Invoice / Tagihan",
        "financial_statement": "Laporan Keuangan",
        "other": "Dokumen Lainnya",
    }
    return labels.get(doc_type, doc_type)
