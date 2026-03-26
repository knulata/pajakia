"""Application-level PII encryption using AES-256-GCM.

Encrypts sensitive fields (NPWP, NIK) at the application layer.
Provides a searchable blind index (SHA-256 hash) for lookups without decryption.
"""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings


def _get_key() -> bytes:
    """Derive a 256-bit key from the configured encryption key."""
    settings = get_settings()
    key_material = settings.encryption_key or settings.secret_key
    return hashlib.sha256(key_material.encode()).digest()


def encrypt_pii(plaintext: str) -> str:
    """Encrypt a PII string. Returns base64-encoded nonce+ciphertext."""
    if not plaintext:
        return ""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_pii(encrypted: str) -> str:
    """Decrypt a PII string from base64-encoded nonce+ciphertext."""
    if not encrypted:
        return ""
    key = _get_key()
    raw = base64.b64decode(encrypted)
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


def pii_search_hash(plaintext: str) -> str:
    """Create a searchable blind index for PII lookups.

    This allows searching by NPWP/NIK without storing plaintext.
    Uses HMAC-like construction with the encryption key as salt.
    """
    if not plaintext:
        return ""
    settings = get_settings()
    salt = (settings.encryption_key or settings.secret_key).encode()
    return hashlib.sha256(salt + plaintext.strip().encode()).hexdigest()
