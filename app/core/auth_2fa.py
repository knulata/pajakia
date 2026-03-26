"""TOTP-based two-factor authentication for consultant accounts."""

import io
import base64
import secrets

import pyotp
import qrcode

from app.core.config import get_settings


def generate_totp_secret() -> str:
    """Generate a new TOTP secret for a user."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Get the otpauth:// URI for QR code generation."""
    settings = get_settings()
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.totp_issuer)


def generate_qr_code_base64(secret: str, email: str) -> str:
    """Generate a QR code image as base64 for the frontend to display."""
    uri = get_totp_uri(secret, email)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret. Allows 1 window of drift."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 8) -> list[str]:
    """Generate one-time backup codes for account recovery."""
    return [secrets.token_hex(4).upper() for _ in range(count)]
