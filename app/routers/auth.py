"""Authentication — Google OAuth, JWT access/refresh tokens, 2FA setup."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_access_token, create_refresh_token, decode_token, get_current_user,
)
from app.core.auth_2fa import (
    generate_totp_secret, generate_qr_code_base64, verify_totp, generate_backup_codes,
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/google/login")
async def google_login():
    """Return the Google OAuth URL for the frontend to redirect to."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{query}"}


@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback — exchange code for token, upsert user."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")
        tokens = token_resp.json()

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        userinfo = userinfo_resp.json()

    # Upsert user
    result = await db.execute(
        select(User).where(User.google_id == userinfo["id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(
            select(User).where(User.email == userinfo["email"])
        )
        user = result.scalar_one_or_none()

    if user:
        user.google_id = userinfo["id"]
        user.name = userinfo.get("name", user.name)
        user.avatar_url = userinfo.get("picture")
    else:
        user = User(
            email=userinfo["email"],
            name=userinfo.get("name", ""),
            google_id=userinfo["id"],
            avatar_url=userinfo.get("picture"),
        )
        db.add(user)

    # Update login tracking
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host if request.client else None

    await db.commit()
    await db.refresh(user)

    # If 2FA is enabled, return a temporary token that requires TOTP verification
    if user.totp_enabled:
        temp_token = create_access_token(
            data={"sub": user.id, "email": user.email, "requires_2fa": True},
        )
        return {
            "requires_2fa": True,
            "temp_token": temp_token,
            "token_type": "bearer",
        }

    # No 2FA — issue full tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "totp_enabled": user.totp_enabled,
        },
    }


# --- 2FA Verification ---

class TOTPVerifyRequest(BaseModel):
    temp_token: str
    code: str


@router.post("/2fa/verify")
async def verify_2fa(data: TOTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify TOTP code to complete login."""
    payload = decode_token(data.temp_token)
    if not payload.get("requires_2fa"):
        raise HTTPException(400, "Token does not require 2FA")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.totp_secret:
        raise HTTPException(400, "2FA not configured")

    if not verify_totp(user.totp_secret, data.code):
        # Check backup codes
        if user.backup_codes and data.code.upper() in user.backup_codes:
            user.backup_codes = [c for c in user.backup_codes if c != data.code.upper()]
            await db.commit()
        else:
            raise HTTPException(401, "Invalid 2FA code")

    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "totp_enabled": user.totp_enabled,
        },
    }


# --- 2FA Setup ---

@router.post("/2fa/setup")
async def setup_2fa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate TOTP secret and QR code for 2FA enrollment."""
    if user.totp_enabled:
        raise HTTPException(400, "2FA already enabled")

    secret = generate_totp_secret()
    qr_base64 = generate_qr_code_base64(secret, user.email)

    user.totp_secret = secret
    await db.commit()

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "message": "Scan QR code with your authenticator app, then call /2fa/confirm with a code to enable.",
    }


class TOTPConfirmRequest(BaseModel):
    code: str


@router.post("/2fa/confirm")
async def confirm_2fa(
    data: TOTPConfirmRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm 2FA setup by verifying a TOTP code. Generates backup codes."""
    if user.totp_enabled:
        raise HTTPException(400, "2FA already enabled")
    if not user.totp_secret:
        raise HTTPException(400, "Call /2fa/setup first")

    if not verify_totp(user.totp_secret, data.code):
        raise HTTPException(400, "Invalid code. Try again.")

    backup_codes = generate_backup_codes()
    user.totp_enabled = True
    user.backup_codes = backup_codes
    await db.commit()

    return {
        "enabled": True,
        "backup_codes": backup_codes,
        "message": "2FA enabled. Save these backup codes securely.",
    }


@router.post("/2fa/disable")
async def disable_2fa(
    data: TOTPConfirmRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable 2FA. Requires current TOTP code."""
    if not user.totp_enabled or not user.totp_secret:
        raise HTTPException(400, "2FA not enabled")

    if not verify_totp(user.totp_secret, data.code):
        raise HTTPException(401, "Invalid code")

    user.totp_enabled = False
    user.totp_secret = None
    user.backup_codes = None
    await db.commit()

    return {"enabled": False, "message": "2FA disabled."}


# --- Token Refresh ---

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for new access + refresh tokens (rotation)."""
    payload = decode_token(data.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or deactivated")

    new_access = create_access_token(data={"sub": user.id, "email": user.email})
    new_refresh = create_refresh_token(data={"sub": user.id, "email": user.email})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


# --- IP Allowlist ---

class IPAllowlistRequest(BaseModel):
    ips: list[str]


@router.put("/ip-allowlist")
async def set_ip_allowlist(
    data: IPAllowlistRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set IP allowlist (optional — pass empty list to disable)."""
    user.ip_allowlist = data.ips if data.ips else None
    await db.commit()
    return {"ip_allowlist": user.ip_allowlist, "message": "IP allowlist updated."}
