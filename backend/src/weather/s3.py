import json, time
from datetime import datetime, timedelta, timezone
import boto3
from .settings import settings

# Create S3 client with explicit credentials from settings
_s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

def put_json_reading(d: dict):
    # key like: raspi-weather/2025-10-06/2025-10-06T20-15-03Z.json
    ts = d["ts"].replace(":", "-")
    date = d["ts"][:10]
    key = f"{settings.s3_prefix}/{date}/{ts}.json"
    _s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=json.dumps(d).encode("utf-8"))

def get_readings_last_n_hours(hours: int = 24) -> list[dict]:
    """
    Retrieve all weather readings from the last N hours from S3.
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        A list of reading dictionaries sorted by timestamp (oldest first).
    """
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(hours=hours)
    
    # We need to check today and potentially yesterday (to handle day boundaries)
    dates_to_check = [
        cutoff_time.strftime("%Y-%m-%d"),
        now.strftime("%Y-%m-%d")
    ]
    
    # Remove duplicates (in case both are the same day)
    dates_to_check = list(set(dates_to_check))
    
    readings = []
    
    for date in dates_to_check:
        prefix = f"{settings.s3_prefix}/{date}/"
        
        try:
            # List all objects with this date prefix
            paginator = _s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=settings.s3_bucket, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    try:
                        # Fetch the object
                        response = _s3.get_object(Bucket=settings.s3_bucket, Key=key)
                        data = json.loads(response['Body'].read().decode('utf-8'))
                        
                        # Parse timestamp and filter by 24h window
                        reading_time = datetime.fromisoformat(data['ts'].replace('Z', '+00:00'))
                        
                        if reading_time >= cutoff_time:
                            readings.append(data)
                            
                    except Exception as e:
                        print(f"Error reading object {key}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error listing objects for date {date}: {e}")
            continue
    
    # Sort by timestamp (oldest first)
    readings.sort(key=lambda x: x['ts'])
    
    return readings
