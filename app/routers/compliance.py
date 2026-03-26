"""Data compliance API — export, deletion, retention, consent management."""

import io
import json
import zipfile
import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.security import get_current_user, get_current_consultant
from app.core.config import get_settings
from app.models.user import User
from app.models.client import Client
from app.models.document import Document
from app.models.tax_filing import TaxFiling
from app.models.whatsapp_message import WhatsAppMessage
from app.models.audit_log import AuditLog
from app.models.consent import ClientConsent, ConsentType, ConsentStatus
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compliance", tags=["compliance"])
settings = get_settings()


@router.get("/export/my-data")
async def export_my_data(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    data = {"user_profile": {"id": user.id, "email": user.email, "name": user.name, "phone": user.phone, "npwp": user.npwp, "role": user.role.value, "created_at": str(user.created_at)}}
    filing_result = await db.execute(select(TaxFiling).where(TaxFiling.user_id == user.id))
    data["tax_filings"] = [{"id": f.id, "type": f.filing_type.value, "status": f.status.value, "tax_year": f.tax_year, "gross_income": float(f.gross_income) if f.gross_income else None, "tax_due": float(f.tax_due) if f.tax_due else None, "created_at": str(f.created_at)} for f in filing_result.scalars().all()]
    doc_result = await db.execute(select(Document).where(Document.user_id == user.id))
    data["documents"] = [{"id": d.id, "type": d.doc_type.value, "status": d.status.value, "file_name": d.file_name, "extracted_data": d.extracted_data, "created_at": str(d.created_at)} for d in doc_result.scalars().all()]
    msg_result = await db.execute(select(WhatsAppMessage).where(WhatsAppMessage.user_id == user.id))
    data["whatsapp_messages"] = [{"direction": m.direction.value, "type": m.message_type.value, "body": m.body, "created_at": str(m.created_at)} for m in msg_result.scalars().all()]
    db.add(AuditLog(user_id=user.id, action="export_data", resource_type="user", resource_id=user.id, detail="Full data export"))
    await db.commit()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("pajakia_export.json", json.dumps(data, indent=2, ensure_ascii=False))
        zf.writestr("README.txt", f"Pajakia Data Export\nGenerated: {datetime.now(timezone.utc).isoformat()}\nUser: {user.email}\n")
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=pajakia_export_{user.id[:8]}.zip"})


@router.get("/export/client/{client_id}")
async def export_client_data(client_id: str, user: User = Depends(get_current_consultant), db: AsyncSession = Depends(get_db)):
    client_result = await db.execute(select(Client).where(Client.id == client_id, Client.consultant_id == user.id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(404, "Client not found")
    data = {"client_profile": {"id": client.id, "name": client.name, "npwp": client.npwp, "nik": client.nik, "email": client.email, "entity_type": client.entity_type.value, "status": client.status.value}}
    if client.user_id:
        filing_result = await db.execute(select(TaxFiling).where(TaxFiling.user_id == client.user_id))
        data["tax_filings"] = [{"type": f.filing_type.value, "status": f.status.value, "tax_year": f.tax_year, "gross_income": float(f.gross_income) if f.gross_income else None, "tax_due": float(f.tax_due) if f.tax_due else None} for f in filing_result.scalars().all()]
        doc_result = await db.execute(select(Document).where(Document.user_id == client.user_id))
        data["documents"] = [{"type": d.doc_type.value, "file_name": d.file_name, "extracted_data": d.extracted_data} for d in doc_result.scalars().all()]
    consent_result = await db.execute(select(ClientConsent).where(ClientConsent.client_id == client_id))
    data["consents"] = [{"type": c.consent_type.value, "status": c.status.value, "granted_at": str(c.granted_at), "evidence": c.evidence} for c in consent_result.scalars().all()]
    db.add(AuditLog(user_id=user.id, action="export_client_data", resource_type="client", resource_id=client_id))
    await db.commit()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("client_export.json", json.dumps(data, indent=2, ensure_ascii=False))
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=client_{client_id[:8]}.zip"})


@router.delete("/delete/my-data")
async def delete_my_data(confirm: bool = Query(False), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not confirm:
        return {"warning": "This will permanently delete ALL your data. Pass ?confirm=true to proceed."}
    user_id = user.id
    await db.execute(delete(WhatsAppMessage).where(WhatsAppMessage.user_id == user_id))
    await db.execute(delete(Document).where(Document.user_id == user_id))
    await db.execute(delete(TaxFiling).where(TaxFiling.user_id == user_id))
    audit_result = await db.execute(select(AuditLog).where(AuditLog.user_id == user_id))
    for log in audit_result.scalars().all():
        log.user_id = None
        log.detail = "[REDACTED]"
    user.is_active = False
    user.email = f"deleted-{user_id[:8]}@pajakia.internal"
    user.name = "[Deleted User]"
    user.phone = None
    user.npwp = None
    user.google_id = None
    user.avatar_url = None
    user.totp_secret = None
    user.backup_codes = None
    db.add(AuditLog(action="delete_user_data", resource_type="user", resource_id=user_id, detail="User requested complete data deletion"))
    await db.commit()
    return {"status": "deleted", "message": "All your data has been permanently deleted."}


@router.delete("/delete/client/{client_id}")
async def delete_client_data(client_id: str, confirm: bool = Query(False), user: User = Depends(get_current_consultant), db: AsyncSession = Depends(get_db)):
    if not confirm:
        return {"warning": "This will permanently delete ALL data for this client. Pass ?confirm=true to proceed."}
    client_result = await db.execute(select(Client).where(Client.id == client_id, Client.consultant_id == user.id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(404, "Client not found")
    if client.user_id:
        await db.execute(delete(Document).where(Document.user_id == client.user_id))
        await db.execute(delete(TaxFiling).where(TaxFiling.user_id == client.user_id))
        await db.execute(delete(WhatsAppMessage).where(WhatsAppMessage.user_id == client.user_id))
    await db.execute(delete(ClientConsent).where(ClientConsent.client_id == client_id))
    await db.execute(delete(Invoice).where(Invoice.client_id == client_id))
    await db.execute(delete(Client).where(Client.id == client_id))
    db.add(AuditLog(user_id=user.id, action="delete_client_data", resource_type="client", resource_id=client_id, detail=f"Deleted client: {client.name}"))
    await db.commit()
    return {"status": "deleted", "client_name": client.name}


@router.get("/retention/status")
async def retention_status(user: User = Depends(get_current_consultant), db: AsyncSession = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.data_retention_years * 365)
    old_docs = await db.execute(select(Document).where(Document.created_at < cutoff).join(Client, Client.user_id == Document.user_id).where(Client.consultant_id == user.id))
    old_count = len(old_docs.scalars().all())
    return {"retention_policy_years": settings.data_retention_years, "cutoff_date": str(cutoff.date()), "documents_past_retention": old_count}


@router.get("/consents/{client_id}")
async def get_client_consents(client_id: str, user: User = Depends(get_current_consultant), db: AsyncSession = Depends(get_db)):
    client_result = await db.execute(select(Client).where(Client.id == client_id, Client.consultant_id == user.id))
    if not client_result.scalar_one_or_none():
        raise HTTPException(404, "Client not found")
    consent_result = await db.execute(select(ClientConsent).where(ClientConsent.client_id == client_id).order_by(ClientConsent.granted_at.desc()))
    return [{"id": c.id, "consent_type": c.consent_type.value, "status": c.status.value, "granted_at": str(c.granted_at), "revoked_at": str(c.revoked_at) if c.revoked_at else None, "evidence": c.evidence} for c in consent_result.scalars().all()]


@router.post("/consents/{client_id}/revoke")
async def revoke_consent(client_id: str, consent_type: str = Query(...), user: User = Depends(get_current_consultant), db: AsyncSession = Depends(get_db)):
    consent_result = await db.execute(select(ClientConsent).where(ClientConsent.client_id == client_id, ClientConsent.consultant_id == user.id, ClientConsent.consent_type == ConsentType(consent_type), ClientConsent.status == ConsentStatus.GRANTED))
    consent = consent_result.scalar_one_or_none()
    if not consent:
        raise HTTPException(404, "Active consent not found")
    consent.status = ConsentStatus.REVOKED
    consent.revoked_at = datetime.now(timezone.utc)
    db.add(AuditLog(user_id=user.id, action="revoke_consent", resource_type="client", resource_id=client_id, detail=f"Revoked: {consent_type}"))
    await db.commit()
    return {"status": "revoked", "consent_type": consent_type}


@router.get("/privacy-info")
async def privacy_info():
    return {
        "data_residency": "Indonesia (ap-southeast-1)",
        "encryption": {"in_transit": "TLS 1.3", "at_rest": "AES-256-GCM (PII fields), S3 SSE (documents)"},
        "data_retention": f"{settings.data_retention_years} years",
        "your_rights": ["Export all your data at any time", "Request complete data deletion", "View who accessed your data", "Revoke consent for data processing"],
        "contact": "privacy@pajakia.com",
    }
