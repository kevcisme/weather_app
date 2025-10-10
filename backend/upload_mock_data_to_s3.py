#!/usr/bin/env python3
"""
Generate mock weather data and upload it directly to S3 with proper folder structure.
This creates data for the last N hours with current timestamps.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import boto3
from weather.settings import settings

def generate_mock_readings(hours=24):
    """Generate realistic mock weather readings for the specified number of hours"""
    readings = []
    
    # Start from current time, going back specified hours
    base_time = datetime.now(timezone.utc) - timedelta(hours=hours-1)
    
    # Base values with some realistic variation
    base_temp_c = 20.0  # Base temperature in Celsius
    base_humidity = 60.0  # Base humidity percentage
    base_pressure = 1013.25  # Base pressure in hPa
    
    for i in range(hours):
        # Calculate timestamp (every hour)
        ts = base_time + timedelta(hours=i)
        
        # Add daily temperature variation (warmer during day, cooler at night)
        # Using sine wave to simulate day/night cycle
        hour_of_day = ts.hour
        temp_variation = 5 * math.sin((hour_of_day - 6) * math.pi / 12)  # Peak at 2 PM
        temp_c = round(base_temp_c + temp_variation + (i % 3 - 1) * 0.5, 2)  # Add some randomness
        temp_f = round(temp_c * 9/5 + 32, 2)
        
        # Humidity inversely related to temperature (roughly)
        humidity = round(base_humidity - temp_variation * 2 + (i % 5 - 2) * 2, 2)
        humidity = max(30, min(90, humidity))  # Keep within reasonable bounds
        
        # Slight pressure variations
        pressure = round(base_pressure + math.sin(i * 0.3) * 5 + (i % 4 - 1.5) * 0.5, 2)
        
        reading = {
            "ts": ts.isoformat().replace("+00:00", "Z"),
            "temp_c": temp_c,
            "temp_f": temp_f,
            "humidity": humidity,
            "pressure": pressure,
        }
        readings.append(reading)
    
    return readings

def upload_to_s3(readings):
    """Upload readings to S3 with proper folder structure"""
    print(f"Uploading {len(readings)} mock readings to S3")
    print(f"Bucket: {settings.s3_bucket}")
    print(f"Prefix: {settings.s3_prefix}")
    print(f"Region: {settings.aws_region}")
    print("=" * 80)
    
    # Create S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    
    uploaded = 0
    failed = 0
    
    for reading in readings:
        try:
            # Create S3 key with date folder structure
            # Format: samples/2025-10-10/2025-10-10T20-15-03.123456Z.json
            ts = reading["ts"].replace(":", "-")
            date = reading["ts"][:10]
            key = f"{settings.s3_prefix}/{date}/{ts}.json"
            
            # Upload to S3
            s3.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=json.dumps(reading).encode("utf-8"),
                ContentType="application/json"
            )
            
            uploaded += 1
            print(f"✅ {uploaded:2d}. {key}")
            print(f"     Temp: {reading['temp_c']}°C / {reading['temp_f']}°F, "
                  f"Humidity: {reading['humidity']}%, "
                  f"Pressure: {reading['pressure']} hPa")
            
        except Exception as e:
            failed += 1
            print(f"❌ Failed to upload {reading['ts']}: {e}")
    
    print("=" * 80)
    print(f"✅ Successfully uploaded {uploaded} readings")
    if failed > 0:
        print(f"❌ Failed to upload {failed} readings")
    
    return uploaded > 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload mock weather data to S3')
    parser.add_argument('--hours', type=int, default=24, 
                        help='Number of hours of data to generate (default: 24)')
    args = parser.parse_args()
    
    print(f"\n📊 Generating {args.hours} hours of mock weather data...\n")
    readings = generate_mock_readings(args.hours)
    
    success = upload_to_s3(readings)
    
    if success:
        print(f"\n🎉 Done! You can now test the API:")
        print(f"   - Latest: http://192.168.86.49:8000/latest")
        print(f"   - History (24h): http://192.168.86.49:8000/history?hours=24")
        print(f"   - History ({args.hours}h): http://192.168.86.49:8000/history?hours={args.hours}")
    
    sys.exit(0 if success else 1)

