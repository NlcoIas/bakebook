"""Cloudflare R2 object storage service.

In dev mode (ENV=dev), stores files locally in /tmp/bakebook-uploads/.
In prod, uses real R2 presigned URLs via boto3.
"""

import uuid
from pathlib import Path

import boto3
from botocore.config import Config

from app.config import settings

_LOCAL_DIR = Path("/tmp/bakebook-uploads")


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def generate_upload_url(bake_id: str, filename: str) -> dict:
    """Generate a presigned PUT URL for uploading a photo."""
    ext = Path(filename).suffix or ".jpg"
    r2_key = f"bakes/{bake_id}/{uuid.uuid4().hex}{ext}"

    if settings.env == "dev":
        _LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        return {
            "r2Key": r2_key,
            "presignedUrl": f"file://{_LOCAL_DIR / r2_key}",
            "expiresIn": 3600,
            "dev": True,
        }

    client = _get_s3_client()
    url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket,
            "Key": r2_key,
            "ContentType": f"image/{ext.lstrip('.')}",
        },
        ExpiresIn=3600,
    )

    return {
        "r2Key": r2_key,
        "presignedUrl": url,
        "expiresIn": 3600,
    }


def generate_read_url(r2_key: str) -> str:
    """Generate a presigned GET URL for reading a photo."""
    if settings.env == "dev":
        return f"file://{_LOCAL_DIR / r2_key}"

    client = _get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.r2_bucket, "Key": r2_key},
        ExpiresIn=3600,
    )


def delete_object(r2_key: str) -> None:
    """Delete an object from R2."""
    if settings.env == "dev":
        path = _LOCAL_DIR / r2_key
        path.unlink(missing_ok=True)
        return

    client = _get_s3_client()
    client.delete_object(Bucket=settings.r2_bucket, Key=r2_key)
