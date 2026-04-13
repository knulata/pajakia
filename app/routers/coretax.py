"""Coretax integration API — XML generation, validation, error decoding, retry queue."""

import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user, get_current_consultant
from app.models.user import User
from app.models.client import Client
from app.models.audit_log import AuditLog
from app.models.coretax_submission import CoretaxSubmission, SubmissionStatus
from app.services.coretax import (
    generate_ebupot_xml,
    generate_efaktur_xml,
    generate_spt_masa_pph21_xml,
    sanitize_npwp,
    sanitize_nik,
    sanitize_filename,
    sanitize_currency,
    sanitize_date,
    validate_ebupot_xml,
    validate_efaktur_xml,
    KNOWN_CORETAX_ERRORS,
    suggest_fix,
)
from app.services.coretax.retry_queue import (
    queue_submission,
    get_pending_submissions,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/coretax", tags=["coretax"])


# ──────────────────────────────────────────
# XML Generation
# ──────────────────────────────────────────

class EbupotRequest(BaseModel):
    bukti_potong: list[dict]
    pemotong_npwp: str
    pemotong_nama: str
    masa: int
    tahun: int


@router.post("/xml/ebupot")
async def xml_ebupot(data: EbupotRequest):
    """Generate Coretax-compatible e-Bupot XML from bukti potong data."""
    xml = generate_ebupot_xml(
        bukti_potong_list=data.bukti_potong,
        pemotong_npwp=data.pemotong_npwp,
        pemotong_nama=data.pemotong_nama,
        masa=data.masa,
        tahun=data.tahun,
    )
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=ebupot_{data.tahun}{data.masa:02d}.xml",
        },
    )


@router.post("/xml/ebupot/preview")
async def xml_ebupot_preview(data: EbupotRequest):
    """Same as /xml/ebupot but returns XML as JSON string for preview (no download)."""
    xml = generate_ebupot_xml(
        bukti_potong_list=data.bukti_potong,
        pemotong_npwp=data.pemotong_npwp,
        pemotong_nama=data.pemotong_nama,
        masa=data.masa,
        tahun=data.tahun,
    )
    validation = validate_ebupot_xml(xml)
    return {
        "xml": xml,
        "validation": {
            "is_valid": validation.is_valid,
            "total_records": validation.total_records,
            "errors": [asdict(e) for e in validation.errors],
            "warnings": [asdict(w) for w in validation.warnings],
        },
    }


class EfakturRequest(BaseModel):
    faktur: list[dict]
    seller_npwp: str
    seller_nama: str
    masa: int
    tahun: int
    ppn_rate: float = 0.11


@router.post("/xml/efaktur")
async def xml_efaktur(data: EfakturRequest):
    """Generate Coretax-compatible e-Faktur XML."""
    xml = generate_efaktur_xml(
        faktur_list=data.faktur,
        seller_npwp=data.seller_npwp,
        seller_nama=data.seller_nama,
        masa=data.masa,
        tahun=data.tahun,
        ppn_rate=data.ppn_rate,
    )
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=efaktur_{data.tahun}{data.masa:02d}.xml",
        },
    )


class SPTMasaPPh21Request(BaseModel):
    employees: list[dict]
    pemotong_npwp: str
    pemotong_nama: str
    masa: int
    tahun: int


@router.post("/xml/spt-masa-pph21")
async def xml_spt_masa_pph21(data: SPTMasaPPh21Request):
    """Generate Coretax SPT Masa PPh 21 XML."""
    xml = generate_spt_masa_pph21_xml(
        employees=data.employees,
        pemotong_npwp=data.pemotong_npwp,
        pemotong_nama=data.pemotong_nama,
        masa=data.masa,
        tahun=data.tahun,
    )
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=spt_masa_pph21_{data.tahun}{data.masa:02d}.xml",
        },
    )


# ──────────────────────────────────────────
# Validation
# ──────────────────────────────────────────

class ValidateRequest(BaseModel):
    xml_content: str
    type: str  # "ebupot" | "efaktur"


@router.post("/validate")
async def validate_xml(data: ValidateRequest):
    """Pre-flight validate XML against the 22 known Coretax errors."""
    if data.type == "ebupot":
        result = validate_ebupot_xml(data.xml_content)
    elif data.type == "efaktur":
        result = validate_efaktur_xml(data.xml_content)
    else:
        raise HTTPException(400, "type must be 'ebupot' or 'efaktur'")

    return {
        "is_valid": result.is_valid,
        "total_records": result.total_records,
        "errors": [asdict(e) for e in result.errors],
        "warnings": [asdict(w) for w in result.warnings],
        "summary": {
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
            "auto_fixable": all(
                KNOWN_CORETAX_ERRORS.get(e.code.replace("ERR-CT-", "").replace("WARN-CT-", ""), {}).get("auto_fixable", False)
                for e in result.errors
            ) if result.errors else True,
        },
    }


# ──────────────────────────────────────────
# Sanitization (single field)
# ──────────────────────────────────────────

class SanitizeRequest(BaseModel):
    npwp: str | None = None
    nik: str | None = None
    filename: str | None = None
    currency: str | None = None
    date: str | None = None


@router.post("/sanitize")
async def sanitize_fields(data: SanitizeRequest):
    """Clean a batch of fields — fixes Excel scientific notation, formats, etc."""
    return {
        "npwp": sanitize_npwp(data.npwp) if data.npwp is not None else None,
        "nik": sanitize_nik(data.nik) if data.nik is not None else None,
        "filename": sanitize_filename(data.filename) if data.filename is not None else None,
        "currency": sanitize_currency(data.currency) if data.currency is not None else None,
        "date": sanitize_date(data.date) if data.date is not None else None,
    }


# ──────────────────────────────────────────
# Error Decoder
# ──────────────────────────────────────────

class ErrorDecodeRequest(BaseModel):
    error_message: str


@router.post("/decode-error")
async def decode_error(data: ErrorDecodeRequest):
    """Paste a Coretax error message, get the explanation and fix."""
    return suggest_fix(data.error_message)


@router.get("/known-errors")
async def list_known_errors():
    """Return the catalog of 22 known Coretax errors with fixes."""
    return {
        "total": len(KNOWN_CORETAX_ERRORS),
        "errors": [
            {"key": k, **v}
            for k, v in KNOWN_CORETAX_ERRORS.items()
        ],
    }


# ──────────────────────────────────────────
# Retry Queue
# ──────────────────────────────────────────

class QueueSubmissionRequest(BaseModel):
    submission_type: str
    xml_content: str
    masa: int
    tahun: int
    client_id: str | None = None


@router.post("/queue")
async def queue_for_upload(
    data: QueueSubmissionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Queue an XML submission to be uploaded to Coretax (with auto-retry)."""
    submission = await queue_submission(
        db=db,
        user_id=user.id,
        submission_type=data.submission_type,
        xml_content=data.xml_content,
        masa=data.masa,
        tahun=data.tahun,
        client_id=data.client_id,
    )

    db.add(AuditLog(
        user_id=user.id, action="queue_coretax_submission",
        resource_type="coretax_submission", resource_id=submission.id,
        detail=f"{data.submission_type} for {data.masa}/{data.tahun}",
    ))
    await db.commit()

    return {
        "id": submission.id,
        "status": submission.status.value,
        "queued_at": str(submission.created_at),
        "next_retry_at": str(submission.next_retry_at) if submission.next_retry_at else None,
    }


@router.get("/queue")
async def list_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(""),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all Coretax submissions for the current user."""
    query = select(CoretaxSubmission).where(CoretaxSubmission.user_id == user.id)

    if status:
        try:
            query = query.where(CoretaxSubmission.status == SubmissionStatus(status))
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(CoretaxSubmission.created_at.desc()).offset(offset).limit(page_size)
    )
    subs = result.scalars().all()

    return {
        "items": [
            {
                "id": s.id,
                "submission_type": s.submission_type,
                "status": s.status.value,
                "masa": s.masa,
                "tahun": s.tahun,
                "retry_count": s.retry_count,
                "next_retry_at": str(s.next_retry_at) if s.next_retry_at else None,
                "last_error": s.last_error,
                "coretax_reference": s.coretax_reference,
                "created_at": str(s.created_at),
                "completed_at": str(s.completed_at) if s.completed_at else None,
            }
            for s in subs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/queue/stats")
async def queue_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stats for Coretax submission queue."""
    result = await db.execute(
        select(CoretaxSubmission.status, func.count())
        .where(CoretaxSubmission.user_id == user.id)
        .group_by(CoretaxSubmission.status)
    )
    counts = {s.value: c for s, c in result.all()}

    return {
        "queued": counts.get("queued", 0),
        "uploading": counts.get("uploading", 0),
        "retrying": counts.get("retrying", 0),
        "succeeded": counts.get("succeeded", 0),
        "failed": counts.get("failed", 0),
        "total": sum(counts.values()),
    }


@router.delete("/queue/{submission_id}")
async def cancel_submission(
    submission_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a queued Coretax submission."""
    result = await db.execute(
        select(CoretaxSubmission).where(
            CoretaxSubmission.id == submission_id,
            CoretaxSubmission.user_id == user.id,
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(404, "Submission not found")

    sub.status = SubmissionStatus.CANCELLED
    sub.next_retry_at = None
    await db.commit()

    return {"id": submission_id, "status": "cancelled"}


# ──────────────────────────────────────────
# Coretax Status (for browser extension)
# ──────────────────────────────────────────

@router.get("/status")
async def coretax_status():
    """Public endpoint — returns current Coretax health status.

    Used by the browser extension to warn users when Coretax is down.
    """
    # In production, this would ping coretax.pajak.go.id and check response.
    # For now, return a static OK with maintenance window info.
    return {
        "status": "operational",
        "last_checked": "2026-04-09T00:00:00Z",
        "known_maintenance": [
            # Example: {"start": "2026-04-15T22:00:00Z", "end": "2026-04-16T06:00:00Z"}
        ],
        "message": "Coretax is operational. Pajakia akan auto-retry jika ada masalah.",
    }
