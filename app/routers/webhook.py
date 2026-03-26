"""WhatsApp webhook receiver — signature verification mandatory."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.services.whatsapp import parse_webhook_payload, verify_webhook_signature
from app.services.message_router import route_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])
settings = get_settings()


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    if not settings.whatsapp_app_secret:
        logger.error("WHATSAPP_APP_SECRET not configured — rejecting webhook")
        raise HTTPException(status_code=500, detail="Webhook security not configured")
    signature = request.headers.get("x-hub-signature-256", "")
    if not verify_webhook_signature(body, signature):
        logger.warning("Invalid webhook signature from %s", request.client.host if request.client else "unknown")
        raise HTTPException(status_code=403, detail="Invalid signature")
    payload = await request.json()
    messages = parse_webhook_payload(payload)
    for msg in messages:
        try:
            await route_message(msg, db)
        except Exception:
            logger.exception("Error processing message %s", msg.get("id"))
    return {"status": "ok"}
