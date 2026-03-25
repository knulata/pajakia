import logging
import os
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Local fallback when S3 is not configured
LOCAL_UPLOAD_DIR = Path("uploads")


def _get_s3_client():
    if not settings.aws_access_key_id:
        return None
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


async def store_document(
    content: bytes,
    filename: str,
    user_id: str,
    mime_type: str = "application/octet-stream",
) -> str:
    """Store a document and return its URL/path."""
    ext = Path(filename).suffix or ".bin"
    key = f"{user_id}/{uuid.uuid4().hex}{ext}"

    s3 = _get_s3_client()
    if s3:
        try:
            s3.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=content,
                ContentType=mime_type,
            )
            return f"s3://{settings.s3_bucket}/{key}"
        except ClientError as e:
            logger.error("S3 upload failed: %s", e)
            raise

    # Local fallback
    local_path = LOCAL_UPLOAD_DIR / key
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(content)
    return str(local_path)


async def get_document(url: str) -> bytes:
    """Retrieve a document by its URL/path."""
    if url.startswith("s3://"):
        bucket, key = url[5:].split("/", 1)
        s3 = _get_s3_client()
        if not s3:
            raise RuntimeError("S3 not configured")
        resp = s3.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()

    # Local file
    return Path(url).read_bytes()
