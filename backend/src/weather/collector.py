import time, json
from datetime import datetime, timezone
from .hat import get_sense, get_cpu_temp
from .s3 import put_json_reading, put_silver_reading, get_readings_from_bronze
from .settings import settings
from .calculations import (
    calculate_dew_point, 
    calculate_pressure_trend, 
    calculate_daily_stats,
    get_comfort_index
)

sense = get_sense()

# Track when we last calculated pressure trend
_last_pressure_calc_time = None

def read_measurement():
    """
    Read and calibrate sensor data (Bronze layer).
    Uses pressure sensor as base (more accurate than humidity sensor).
    Applies both static offset and dynamic CPU temperature compensation.
    """
    # Get all temperature readings
    temp_from_humidity = sense.get_temperature_from_humidity()
    temp_from_pressure = sense.get_temperature_from_pressure()
    
    # Use pressure sensor as base (typically more accurate for ambient temp)
    base_temp_c = temp_from_pressure
    
    # Apply static calibration offset
    calibrated_temp_c = base_temp_c - settings.temp_calibration_offset_c
    
    # Optionally apply dynamic CPU compensation
    cpu_temp = get_cpu_temp()
    if cpu_temp and settings.use_cpu_compensation:
        # Additional compensation based on CPU heat (typically 0-2°C extra)
        cpu_factor = (cpu_temp - 50.0) / 30.0  # Normalize CPU temp impact
        cpu_compensation = max(0, cpu_factor * settings.cpu_temp_factor_c)
        calibrated_temp_c -= cpu_compensation
    
    return {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "temp_c": round(calibrated_temp_c, 2),
        "temp_f": round(1.8 * calibrated_temp_c + 32, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2),
        # Debug/diagnostic fields
        "temp_from_humidity": round(temp_from_humidity, 2),
        "temp_from_pressure": round(temp_from_pressure, 2),
        "cpu_temp": round(cpu_temp, 2) if cpu_temp else None,
    }


def create_silver_reading(bronze_reading: dict) -> dict:
    """
    Create enriched silver reading from bronze data with calculated metrics.
    
    Args:
        bronze_reading: Raw sensor reading from read_measurement()
    
    Returns:
        Enriched reading with calculated metrics
    """
    global _last_pressure_calc_time
    
    # Start with bronze data
    silver = bronze_reading.copy()
    
    # 1. Calculate dew point (real-time)
    dew_point = calculate_dew_point(bronze_reading["temp_c"], bronze_reading["humidity"])
    silver.update(dew_point)
    
    # 2. Calculate comfort index
    silver["comfort_index"] = get_comfort_index(
        bronze_reading["temp_f"], 
        bronze_reading["humidity"],
        dew_point["dew_point_f"]
    )
    
    # 3. Calculate pressure trend (every 6 hours)
    current_time = datetime.now(timezone.utc)
    should_calc_pressure = (
        _last_pressure_calc_time is None or 
        (current_time - _last_pressure_calc_time).total_seconds() >= 6 * 3600
    )
    
    if should_calc_pressure:
        # Fetch last 7 hours of bronze data for pressure trend calculation
        historical = get_readings_from_bronze(hours=7)
        pressure_trend = calculate_pressure_trend(bronze_reading, historical)
        _last_pressure_calc_time = current_time
    else:
        # Use previous values or None if not yet calculated
        pressure_trend = {
            "pressure_trend_3h": None,
            "pressure_trend_6h": None,
            "pressure_trend_label": "calculating"
        }
    
    silver.update(pressure_trend)
    
    # 4. Calculate daily stats (rolling calculation)
    # Fetch today's bronze readings from S3
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    hours_since_midnight = (current_time - today_start).total_seconds() / 3600
    todays_readings = get_readings_from_bronze(hours=int(hours_since_midnight) + 1)
    
    # Filter to only today's readings
    today_str = today_start.strftime("%Y-%m-%d")
    print(f"Daily stats calc: Looking for readings from {today_str}, found {len(todays_readings)} total readings", flush=True)
    todays_readings = [r for r in todays_readings if r["ts"].startswith(today_str)]
    print(f"After filtering to today: {len(todays_readings)} readings", flush=True)
    
    # Include the current reading in the daily stats (important for accuracy and early-day data)
    todays_readings.append(bronze_reading)
    print(f"After including current reading: {len(todays_readings)} readings", flush=True)
    
    daily_stats = calculate_daily_stats(todays_readings)
    print(f"Calculated daily stats: {daily_stats}", flush=True)
    silver.update(daily_stats)
    
    return silver

if __name__ == "__main__":
    while True:
        # Read raw measurement (Bronze)
        bronze = read_measurement()
        print(f"Bronze: {json.dumps(bronze)}", flush=True)
        
        try:
            # Write to bronze layer
            put_json_reading(bronze)
            print("✓ Bronze written", flush=True)
            
            # Create and write enriched silver reading
            silver = create_silver_reading(bronze)
            put_silver_reading(silver)
            print(f"✓ Silver written (comfort: {silver.get('comfort_index')}, "
                  f"pressure_trend: {silver.get('pressure_trend_label')})", flush=True)
            
        except Exception as e:
            print(f"S3 upload error: {e}", flush=True)
        
        time.sleep(settings.sample_interval_sec)
