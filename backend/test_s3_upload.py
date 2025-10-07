#!/usr/bin/env python3
"""
Test script for S3 upload functionality.
This creates a test reading and uploads it to S3.
"""
import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather.s3 import put_json_reading
from datetime import datetime, timezone

def test_upload():
    """Upload a test reading to S3"""
    test_reading = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "temp_c": 22.5,
        "temp_f": 72.5,
        "humidity": 55.0,
        "pressure": 1013.25,
    }
    
    print(f"Attempting to upload test reading: {test_reading}")
    
    try:
        put_json_reading(test_reading)
        print(f"✅ Successfully uploaded to S3!")
        print(f"\nCheck your S3 bucket for:")
        date = test_reading["ts"][:10]
        ts = test_reading["ts"].replace(":", "-")
        print(f"  Bucket: From your .env S3_BUCKET setting")
        print(f"  Key: <S3_PREFIX>/{date}/{ts}.json")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check that .env file exists in backend/src/weather/")
        print("2. Verify AWS credentials are set correctly")
        print("3. Ensure S3 bucket name and region are correct")
        print("4. Check that IAM user has s3:PutObject permission")
        return False
    
    return True

if __name__ == "__main__":
    success = test_upload()
    sys.exit(0 if success else 1)
