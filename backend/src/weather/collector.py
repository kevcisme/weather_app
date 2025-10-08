import time, json
from datetime import datetime, timezone
from .hat import get_sense
from .s3 import put_json_reading
from .settings import settings

sense = get_sense()

def read_measurement():
    # Apply calibration offset to compensate for CPU heat
    raw_temp_c = sense.get_temperature()
    calibrated_temp_c = raw_temp_c - settings.temp_calibration_offset_c
    
    return {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "temp_c": round(calibrated_temp_c, 2),
        "temp_f": round(1.8 * calibrated_temp_c + 32, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2),
        "temp_from_cpu": round(raw_temp_c, 2),
        "temp_from_humidity": round(sense.get_temperature_from_humidity(), 2),
        "temp_from_pressure": round(sense.get_temperature_from_pressure(), 2),
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
