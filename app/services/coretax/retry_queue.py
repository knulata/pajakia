"""Coretax retry queue — track failed uploads and auto-retry when Coretax is back up.

Coretax is frequently down for maintenance. Instead of failing, we queue submissions
and retry them automatically with exponential backoff.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.coretax_submission import CoretaxSubmission, SubmissionStatus

logger = logging.getLogger(__name__)

# Exponential backoff schedule (minutes)
RETRY_SCHEDULE = [5, 15, 30, 60, 120, 240, 480, 1440]  # max 24h
MAX_RETRIES = len(RETRY_SCHEDULE)


def next_retry_at(retry_count: int) -> datetime:
    """Compute the next retry timestamp based on attempt count."""
    if retry_count >= MAX_RETRIES:
        return datetime.now(timezone.utc) + timedelta(days=1)
    delay_minutes = RETRY_SCHEDULE[retry_count]
    return datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)


async def queue_submission(
    db: AsyncSession,
    user_id: str,
    submission_type: str,  # "ebupot" | "efaktur" | "spt_masa_pph21"
    xml_content: str,
    masa: int,
    tahun: int,
    client_id: str | None = None,
) -> CoretaxSubmission:
    """Queue a Coretax submission for upload (or retry)."""
    submission = CoretaxSubmission(
        user_id=user_id,
        client_id=client_id,
        submission_type=submission_type,
        xml_content=xml_content,
        masa=masa,
        tahun=tahun,
        status=SubmissionStatus.QUEUED,
        retry_count=0,
        next_retry_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def get_pending_submissions(db: AsyncSession, limit: int = 50) -> list[CoretaxSubmission]:
    """Get all submissions ready to be retried (next_retry_at <= now)."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(CoretaxSubmission).where(
            and_(
                CoretaxSubmission.status.in_([SubmissionStatus.QUEUED, SubmissionStatus.RETRYING]),
                CoretaxSubmission.next_retry_at <= now,
                CoretaxSubmission.retry_count < MAX_RETRIES,
            )
        ).limit(limit)
    )
    return list(result.scalars().all())


async def mark_failed(
    db: AsyncSession,
    submission: CoretaxSubmission,
    error_message: str,
):
    """Mark submission as failed and schedule next retry."""
    submission.retry_count += 1
    submission.last_error = error_message
    submission.last_attempted_at = datetime.now(timezone.utc)

    if submission.retry_count >= MAX_RETRIES:
        submission.status = SubmissionStatus.FAILED
        submission.next_retry_at = None
        logger.warning("Coretax submission %s exceeded max retries", submission.id)
    else:
        submission.status = SubmissionStatus.RETRYING
        submission.next_retry_at = next_retry_at(submission.retry_count)
        logger.info(
            "Coretax submission %s scheduled for retry %d at %s",
            submission.id, submission.retry_count, submission.next_retry_at,
        )

    await db.commit()


async def mark_succeeded(
    db: AsyncSession,
    submission: CoretaxSubmission,
    coretax_reference: str | None = None,
):
    """Mark submission as successfully uploaded to Coretax."""
    submission.status = SubmissionStatus.SUCCEEDED
    submission.coretax_reference = coretax_reference
    submission.completed_at = datetime.now(timezone.utc)
    submission.next_retry_at = None
    await db.commit()
    logger.info("Coretax submission %s succeeded (ref: %s)", submission.id, coretax_reference)


async def process_retry_queue(db: AsyncSession, upload_callback) -> dict:
    """Process all pending submissions. upload_callback receives (xml_content, type) → result."""
    pending = await get_pending_submissions(db)
    succeeded = 0
    failed = 0
    skipped = 0

    for sub in pending:
        try:
            result = await upload_callback(sub.xml_content, sub.submission_type)
            if result.get("success"):
                await mark_succeeded(db, sub, result.get("reference"))
                succeeded += 1
            else:
                await mark_failed(db, sub, result.get("error", "Unknown error"))
                failed += 1
        except Exception as e:
            await mark_failed(db, sub, f"Retry exception: {e}")
            skipped += 1
            await asyncio.sleep(1)  # avoid hammering Coretax

    return {
        "processed": len(pending),
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
    }
