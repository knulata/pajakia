"""Google OAuth authentication router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User

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
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback — exchange code for token, upsert user."""
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
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

        # Get user info
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
        # Check if email exists (e.g., from WhatsApp registration)
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

    await db.commit()
    await db.refresh(user)

    # Create JWT
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
        },
    }
