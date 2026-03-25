import hashlib
import hmac
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GRAPH_API_URL = "https://graph.facebook.com/v21.0"


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify that the webhook request came from Meta."""
    expected = hmac.new(
        settings.whatsapp_app_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def parse_webhook_payload(payload: dict) -> list[dict]:
    """Extract messages from a WhatsApp webhook payload."""
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "messages" not in value:
                continue
            contacts = {
                c["wa_id"]: c.get("profile", {}).get("name", "")
                for c in value.get("contacts", [])
            }
            for msg in value["messages"]:
                messages.append({
                    "id": msg["id"],
                    "from": msg["from"],
                    "from_name": contacts.get(msg["from"], ""),
                    "timestamp": msg["timestamp"],
                    "type": msg["type"],
                    "text": msg.get("text", {}).get("body"),
                    "image": msg.get("image"),
                    "document": msg.get("document"),
                    "interactive": msg.get("interactive"),
                    "context": msg.get("context"),
                })
    return messages


async def send_text_message(to: str, text: str, reply_to: str | None = None) -> dict:
    """Send a text message via WhatsApp."""
    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    if reply_to:
        payload["context"] = {"message_id": reply_to}
    return await _send(payload)


async def send_interactive_buttons(
    to: str,
    body_text: str,
    buttons: list[dict[str, str]],
    header: str | None = None,
    footer: str | None = None,
) -> dict:
    """Send an interactive button message (max 3 buttons)."""
    action_buttons = [
        {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
        for b in buttons[:3]
    ]
    interactive: dict[str, Any] = {
        "type": "button",
        "body": {"text": body_text},
        "action": {"buttons": action_buttons},
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    return await _send({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    })


async def send_interactive_list(
    to: str,
    body_text: str,
    button_text: str,
    sections: list[dict],
    header: str | None = None,
) -> dict:
    """Send an interactive list message."""
    interactive: dict[str, Any] = {
        "type": "list",
        "body": {"text": body_text},
        "action": {"button": button_text[:20], "sections": sections},
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}

    return await _send({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    })


async def download_media(media_id: str) -> bytes:
    """Download media from WhatsApp (images, documents)."""
    async with httpx.AsyncClient() as client:
        # Get media URL
        resp = await client.get(
            f"{GRAPH_API_URL}/{media_id}",
            headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
        )
        resp.raise_for_status()
        media_url = resp.json()["url"]

        # Download the actual file
        resp = await client.get(
            media_url,
            headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
        )
        resp.raise_for_status()
        return resp.content


async def _send(payload: dict) -> dict:
    """Send a message via the WhatsApp Cloud API."""
    url = f"{GRAPH_API_URL}/{settings.whatsapp_phone_number_id}/messages"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.whatsapp_token}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        result = resp.json()
        logger.info("WhatsApp message sent: %s", result)
        return result
