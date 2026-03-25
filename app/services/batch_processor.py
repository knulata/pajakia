"""Batch processing — process multiple documents/filings in parallel."""

import asyncio
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from app.services.ocr import extract_bukti_potong, extract_faktur_pajak
from app.services.anomaly_detector import detect_pph21_anomalies, Anomaly
from app.services.spt_generator import BuktiPotongData
from app.services.document_store import get_document

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    total: int
    success: int
    failed: int
    items: list[dict]
    started_at: str
    completed_at: str


@dataclass
class BatchItem:
    document_id: str
    file_url: str
    status: str  # processing, success, failed
    doc_type: str | None = None
    extracted_data: dict | None = None
    anomalies: list[dict] | None = None
    error: str | None = None


async def process_batch_ocr(
    documents: list[dict],
    max_concurrent: int = 5,
) -> BatchResult:
    """Process multiple documents through OCR in parallel.

    Each document dict should have: id, file_url, doc_type, mime_type
    """
    started_at = datetime.now(timezone.utc).isoformat()
    semaphore = asyncio.Semaphore(max_concurrent)
    items: list[BatchItem] = []

    async def process_one(doc: dict) -> BatchItem:
        async with semaphore:
            item = BatchItem(
                document_id=doc["id"],
                file_url=doc["file_url"],
                status="processing",
                doc_type=doc.get("doc_type"),
            )
            try:
                content = await get_document(doc["file_url"])
                mime = doc.get("mime_type", "image/jpeg")
                doc_type = doc.get("doc_type", "bukti_potong_1721_a1")

                if "faktur" in doc_type:
                    extracted = await extract_faktur_pajak(content, mime)
                else:
                    extracted = await extract_bukti_potong(content, mime)

                if extracted.get("error") or extracted.get("parse_error"):
                    item.status = "failed"
                    item.error = extracted.get("error") or "Failed to parse OCR result"
                else:
                    item.status = "success"
                    item.extracted_data = extracted

                    # Run anomaly detection on bukti potong
                    if "faktur" not in doc_type and "penghasilan_bruto" in extracted:
                        bp = extracted.get("penghasilan_bruto", {})
                        calc = extracted.get("perhitungan_pph", {})
                        anomalies = detect_pph21_anomalies(
                            gross_income=bp.get("total_bruto", 0),
                            pph_dipotong=calc.get("pph21_telah_dipotong", 0),
                            status_ptkp=extracted.get("status_ptkp", ""),
                            biaya_jabatan=extracted.get("pengurang", {}).get("biaya_jabatan", 0),
                            iuran_pensiun=extracted.get("pengurang", {}).get("iuran_pensiun", 0),
                            neto=calc.get("neto_setahun", 0),
                            employer_name=extracted.get("nama_pemotong", ""),
                        )
                        if anomalies:
                            item.anomalies = [asdict(a) for a in anomalies]

            except Exception as e:
                logger.error("Batch OCR failed for %s: %s", doc["id"], e)
                item.status = "failed"
                item.error = str(e)

            return item

    tasks = [process_one(doc) for doc in documents]
    items = await asyncio.gather(*tasks)

    completed_at = datetime.now(timezone.utc).isoformat()
    success = sum(1 for i in items if i.status == "success")

    return BatchResult(
        total=len(documents),
        success=success,
        failed=len(documents) - success,
        items=[asdict(i) for i in items],
        started_at=started_at,
        completed_at=completed_at,
    )


def ocr_to_bukti_potong(extracted: dict) -> BuktiPotongData:
    """Convert raw OCR extraction to structured BuktiPotongData."""
    bp = extracted.get("penghasilan_bruto", {})
    pengurang = extracted.get("pengurang", {})
    calc = extracted.get("perhitungan_pph", {})

    return BuktiPotongData(
        jenis=extracted.get("jenis_formulir", "1721-A1"),
        npwp_pemotong=extracted.get("npwp_pemotong", ""),
        nama_pemotong=extracted.get("nama_pemotong", ""),
        gaji=bp.get("gaji", 0) or 0,
        tunjangan_pph=bp.get("tunjangan_pph", 0) or 0,
        tunjangan_lainnya=bp.get("tunjangan_lainnya", 0) or 0,
        honorarium=bp.get("honorarium", 0) or 0,
        premi_asuransi=bp.get("premi_asuransi", 0) or 0,
        natura=bp.get("natura", 0) or 0,
        bonus_thr=bp.get("bonus_thr", 0) or 0,
        total_bruto=bp.get("total_bruto", 0) or 0,
        biaya_jabatan=pengurang.get("biaya_jabatan", 0) or 0,
        iuran_pensiun=pengurang.get("iuran_pensiun", 0) or 0,
        neto=calc.get("neto_setahun", 0) or calc.get("total_neto", 0) or 0,
        pph21_dipotong=calc.get("pph21_telah_dipotong", 0) or 0,
        nomor_bukti_potong=extracted.get("nomor_bukti_potong", ""),
        masa_pajak=extracted.get("masa_pajak", "01-12"),
    )


async def batch_generate_spt(
    clients_data: list[dict],
    max_concurrent: int = 5,
) -> list[dict]:
    """Generate SPT for multiple clients in parallel.

    Each client dict: client_id, bukti_potong_extractions: list[dict], user_data: dict
    """
    from app.services.spt_generator import generate_spt_1770ss, generate_spt_1770s

    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_one(client: dict) -> dict:
        async with semaphore:
            try:
                bp_list = [
                    ocr_to_bukti_potong(ext)
                    for ext in client["bukti_potong_extractions"]
                ]
                user_data = client["user_data"]
                total_bruto = sum(bp.total_bruto for bp in bp_list)

                # Choose form type
                if len(bp_list) == 1 and total_bruto < 60_000_000:
                    spt = generate_spt_1770ss(bp_list, user_data)
                else:
                    spt = generate_spt_1770s(bp_list, user_data)

                return {
                    "client_id": client["client_id"],
                    "status": "success",
                    "spt_type": "1770SS" if total_bruto < 60_000_000 and len(bp_list) == 1 else "1770S",
                    "spt_data": asdict(spt),
                }
            except Exception as e:
                logger.error("SPT generation failed for %s: %s", client.get("client_id"), e)
                return {
                    "client_id": client["client_id"],
                    "status": "failed",
                    "error": str(e),
                }

    tasks = [generate_one(c) for c in clients_data]
    results = await asyncio.gather(*tasks)
    return list(results)
