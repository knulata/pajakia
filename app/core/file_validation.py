"""File upload validation — whitelist MIME types and scan headers."""

from fastapi import HTTPException, UploadFile

# Only allow these MIME types for tax document uploads
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

# Maximum file size: 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024

# Magic bytes for file type verification
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp",
    b"%PDF": "application/pdf",
}


async def validate_upload(file: UploadFile) -> bytes:
    """Validate file type and size, return file bytes.

    Raises HTTPException if validation fails.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. "
                   f"Accepted: JPEG, PNG, WebP, PDF.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(content) // (1024*1024)}MB). Maximum: 20MB.",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    # Verify magic bytes match declared type
    detected_type = None
    for magic, mime in MAGIC_BYTES.items():
        if content[:len(magic)] == magic:
            detected_type = mime
            break

    if detected_type and detected_type != file.content_type:
        raise HTTPException(
            status_code=400,
            detail="File content does not match declared type.",
        )

    return content
