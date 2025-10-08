import time, json
from datetime import datetime, timezone
from .hat import get_sense, get_cpu_temp
from .s3 import put_json_reading
from .settings import settings

sense = get_sense()

def read_measurement():
    """
    Read and calibrate sensor data.
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

if __name__ == "__main__":
    while True:
        d = read_measurement()
        print(json.dumps(d), flush=True)
        try:
            put_json_reading(d)
        except Exception as e:
            print(f"S3 upload error: {e}", flush=True)
        time.sleep(settings.sample_interval_sec)
