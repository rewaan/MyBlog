import os
import boto3
from botocore.client import Config
from uuid import uuid4

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "blog-media")
S3_PUBLIC_BASE_URL = os.getenv("S3_PUBLIC_BASE_URL")  # jeśli używasz publicznego bucketa lub CDN

s3 = boto3.resource(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

def ensure_bucket():
    try:
        s3.create_bucket(Bucket=S3_BUCKET)
    except Exception:
        pass

def upload_bytes(data: bytes, filename: str) -> str:
    ensure_bucket()
    key = f"{uuid4().hex}_{filename}"
    s3.Bucket(S3_BUCKET).put_object(Key=key, Body=data)
    # Dev (MinIO) — budujemy URL z endpointu
    if S3_PUBLIC_BASE_URL:
        base = S3_PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{key}"
    # fallback (może nie być dostępny publicznie)
    endpoint = S3_ENDPOINT.rstrip("/")
    return f"{endpoint}/{S3_BUCKET}/{key}"
