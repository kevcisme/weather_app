import json, time
import boto3
from .settings import settings

_s3 = boto3.client("s3", region_name=settings.aws_region)

def put_json_reading(d: dict):
    # key like: raspi-weather/2025-10-06/2025-10-06T20-15-03Z.json
    ts = d["ts"].replace(":", "-")
    date = d["ts"][:10]
    key = f"{settings.s3_prefix}/{date}/{ts}.json"
    _s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=json.dumps(d).encode("utf-8"))
