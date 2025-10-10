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

def get_latest_reading_from_s3() -> dict | None:
    """
    Retrieve the most recent weather reading from S3.
    Checks today and yesterday's folders.
    
    Returns:
        The most recent reading dictionary, or None if no readings found.
    """
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    
    # Check both today and yesterday (most recent data likely in today)
    dates_to_check = [
        now.strftime("%Y-%m-%d"),
        yesterday.strftime("%Y-%m-%d")
    ]
    
    latest_reading = None
    latest_time = None
    
    for date in dates_to_check:
        prefix = f"{settings.s3_prefix}/{date}/"
        
        try:
            # List all objects with this date prefix
            response = _s3.list_objects_v2(
                Bucket=settings.s3_bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                continue
            
            # Sort by LastModified to get most recent first
            objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            
            # Check the most recent objects from this date
            for obj in objects[:10]:  # Check top 10 to be safe
                try:
                    key = obj['Key']
                    obj_response = _s3.get_object(Bucket=settings.s3_bucket, Key=key)
                    data = json.loads(obj_response['Body'].read().decode('utf-8'))
                    
                    reading_time = datetime.fromisoformat(data['ts'].replace('Z', '+00:00'))
                    
                    if latest_time is None or reading_time > latest_time:
                        latest_time = reading_time
                        latest_reading = data
                        
                except Exception as e:
                    print(f"Error reading object {key}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error listing objects for date {date}: {e}")
            continue
    
    return latest_reading

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
    
    # Generate all dates between cutoff and now
    # This ensures we check all days that might contain relevant readings
    dates_to_check = []
    current = cutoff_time
    while current <= now:
        date_str = current.strftime("%Y-%m-%d")
        if date_str not in dates_to_check:
            dates_to_check.append(date_str)
        current += timedelta(days=1)
    
    readings = []
    
    print(f"Fetching {hours}h history. Checking dates: {dates_to_check}", flush=True)
    print(f"Using bucket: {settings.s3_bucket}, prefix: {settings.s3_prefix}", flush=True)
    
    for date in dates_to_check:
        prefix = f"{settings.s3_prefix}/{date}/"
        
        try:
            # List all objects with this date prefix
            paginator = _s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=settings.s3_bucket, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    print(f"No contents found for prefix: {prefix}", flush=True)
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
    
    print(f"Found {len(readings)} readings in last {hours}h", flush=True)
    
    return readings
