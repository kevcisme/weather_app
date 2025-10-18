#!/usr/bin/env python3
"""
Test script for WeatherDataReader to verify it works correctly.
"""

import os
from weather_data_reader import WeatherDataReader

def test_reader():
    """Test the WeatherDataReader with sample data."""

    # Initialize reader (you'll need to update these with your actual values)
    reader = WeatherDataReader(
        bucket=os.getenv('AWS_BUCKET_NAME', 'your-bucket-name'),
        bronze_prefix="samples",
        silver_prefix="silver",
        region="us-west-2"
    )

    print("✓ WeatherDataReader initialized")

    # Test listing available dates
    print("\nTesting list_available_dates...")
    try:
        dates = reader.list_available_dates(layer="silver")
        print(f"Found {len(dates)} available dates:")
        print(f"First few: {dates[:5]}")
        print(f"Last few: {dates[-5:]}")
    except Exception as e:
        print(f"Error listing dates: {e}")

    # Test getting recent data
    print("\nTesting get_readings (last 1 hour)...")
    try:
        df = reader.get_readings(hours=1, layer="silver")
        print(f"Loaded {len(df)} readings from the last hour")
        if not df.empty:
            print(f"Columns: {list(df.columns)}")
            print(f"First reading timestamp: {df['timestamp'].min()}")
            print(f"Last reading timestamp: {df['timestamp'].max()}")
        else:
            print("No data found in the last hour")
    except Exception as e:
        print(f"Error getting recent readings: {e}")

    # Test getting latest reading
    print("\nTesting get_latest_reading...")
    try:
        latest = reader.get_latest_reading(layer="silver")
        if latest:
            print("Latest reading found:")
            for key, value in latest.items():
                print(f"  {key}: {value}")
        else:
            print("No latest reading found")
    except Exception as e:
        print(f"Error getting latest reading: {e}")

    print("\n✓ Test completed")

if __name__ == "__main__":
    test_reader()
