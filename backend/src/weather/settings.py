from pydantic import BaseModel
import os

class Settings(BaseModel):
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    s3_bucket: str = os.getenv("S3_BUCKET", "raspi-weather")
    s3_prefix: str = os.getenv("S3_PREFIX", "samples")
    sample_interval_sec: int = int(os.getenv("SAMPLE_INTERVAL_SEC", "900")) # i picked every 15 minutes here, just because round

settings = Settings()
