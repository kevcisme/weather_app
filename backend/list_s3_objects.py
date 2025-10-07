#!/usr/bin/env python3
"""
List objects in the S3 bucket to verify uploads are working.
"""
import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import boto3
from weather.settings import settings

def list_objects():
    """List all objects in the S3 bucket with the configured prefix"""
    print(f"Checking S3 bucket: {settings.s3_bucket}")
    print(f"Prefix: {settings.s3_prefix}")
    print(f"Region: {settings.aws_region}")
    print("-" * 60)
    
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        
        # List objects with prefix
        response = s3.list_objects_v2(
            Bucket=settings.s3_bucket,
            Prefix=settings.s3_prefix
        )
        
        if 'Contents' not in response:
            print("⚠️  No objects found in bucket with this prefix")
            print("\nPossible reasons:")
            print("1. Service hasn't been restarted yet (run: sudo systemctl restart weather)")
            print("2. No readings have been collected yet (15 min interval)")
            print("3. S3 upload is failing (check service logs: journalctl -u weather -f)")
            return False
        
        objects = response['Contents']
        print(f"✅ Found {len(objects)} object(s):\n")
        
        for obj in sorted(objects, key=lambda x: x['LastModified'], reverse=True)[:10]:
            print(f"  📄 {obj['Key']}")
            print(f"     Size: {obj['Size']} bytes, Modified: {obj['LastModified']}")
        
        if len(objects) > 10:
            print(f"\n  ... and {len(objects) - 10} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing S3: {e}")
        print("\nTroubleshooting:")
        print("1. Check AWS credentials in .env file")
        print("2. Verify bucket name and region")
        print("3. Ensure IAM user has s3:ListBucket permission")
        return False

if __name__ == "__main__":
    success = list_objects()
    sys.exit(0 if success else 1)
