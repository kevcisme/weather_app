#!/usr/bin/env python3
"""
Generate 24 hours worth of mock weather data for testing.
Creates individual JSON files in the format expected by S3.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math

def generate_mock_readings(hours=24):
    """Generate realistic mock weather readings for the specified number of hours"""
    readings = []
    
    # Start from current time, going back 24 hours
    base_time = datetime.now(timezone.utc) - timedelta(hours=hours-1)
    
    # Base values with some realistic variation
    base_temp_c = 20.0  # Base temperature in Celsius
    base_humidity = 60.0  # Base humidity percentage
    base_pressure = 1013.25  # Base pressure in hPa
    
    for i in range(hours):
        # Calculate timestamp
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

def save_readings_to_files(readings, output_dir="mock_data"):
    """Save each reading to a separate JSON file"""
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    print(f"Creating {len(readings)} mock data files in {output_path}/")
    print(f"=" * 60)
    
    for i, reading in enumerate(readings, 1):
        # Create filename from timestamp (replace colons with hyphens for filesystem)
        ts_filename = reading["ts"].replace(":", "-")
        filename = f"{ts_filename}.json"
        filepath = output_path / filename
        
        # Write JSON file
        with open(filepath, 'w') as f:
            json.dump(reading, f, indent=2)
        
        print(f"{i:2d}. {filename}")
        print(f"    Temp: {reading['temp_c']}°C / {reading['temp_f']}°F, "
              f"Humidity: {reading['humidity']}%, "
              f"Pressure: {reading['pressure']} hPa")
    
    print(f"=" * 60)
    print(f"✅ Successfully created {len(readings)} files in {output_path}/")
    print(f"\nTo upload these to S3, you can:")
    print(f"1. Use AWS CLI: aws s3 cp {output_path}/ s3://YOUR_BUCKET/PREFIX/ --recursive")
    print(f"2. Or upload individually through AWS Console")

if __name__ == "__main__":
    readings = generate_mock_readings(24)
    save_readings_to_files(readings)
